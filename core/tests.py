import re
import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Customer, Inquiry, Product
from .views import _client_ip

VALID_PAYLOAD = {
    "name": "Ali Rezaei",
    "company": "Alborz Textile",
    "phone": "09121234567",
    "email": "ali@example.com",
    "machine": "Picanol GTX",
    "message": "I need one nozzle.",
}

CLUB_PAYLOAD = {
    "form_type": "club",
    "first_name": "Maryam",
    "last_name": "Ahmadi",
    "company": "Alborz Textile",
    "phone": "\u06f0\u06f9\u06f1\u06f2\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7",
    "email": "maryam@example.com",
}


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ParsStore")
        self.assertContains(response, "PICANOL")

    def test_home_page_has_security_headers(self):
        response = self.client.get(reverse("core:home"))

        self.assertIn("Content-Security-Policy", response)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertIn("camera=()", response["Permissions-Policy"])
        # No external sources are allowed by the CSP
        self.assertNotIn("http", response["Content-Security-Policy"].split("default-src")[1])

    def test_contact_form_is_present(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, 'class="inquiry-form"')
        self.assertContains(response, "hp-input")

    def test_theme_switcher_is_rendered(self):
        response = self.client.get(reverse("core:home"))
        html = response.content.decode()

        self.assertIn('data-theme="dark"', html)
        self.assertIn('data-theme-mode="dark"', html)
        self.assertIn("core/js/theme.js", html)
        self.assertEqual(html.count("data-theme-choice="), 3)
        for mode in ("auto", "light", "dark"):
            self.assertIn(f'data-theme-choice="{mode}"', html)

    def test_csp_allows_no_inline_scripts(self):
        response = self.client.get(reverse("core:home"))

        script_policy = [
            part
            for part in response["Content-Security-Policy"].split(";")
            if part.strip().startswith("script-src")
        ]
        self.assertEqual(len(script_policy), 1)
        self.assertNotIn("'unsafe-inline'", script_policy[0])

    def test_language_switcher_is_rendered(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response["Content-Language"], "en")
        self.assertContains(response, 'class="language-switch"')
        for code in ("en", "de"):
            self.assertContains(response, f'href="/?lang={code}"')

    def test_about_text_interpolates_the_founding_year(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "spare parts since 2006.")
        self.assertNotContains(response, "{since}")


class InquiryFormTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_inquiry_form_saves_request(self):
        response = self.client.post(reverse("core:home"), VALID_PAYLOAD, follow=True)

        self.assertRedirects(response, f"{reverse('core:home')}?lang=en#contact")
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertContains(response, "Your inquiry was received.")

        inquiry = Inquiry.objects.first()
        self.assertEqual(inquiry.name, "Ali Rezaei")
        self.assertEqual(inquiry.phone, "09121234567")
        self.assertEqual(inquiry.email, "ali@example.com")

    def test_company_and_machine_are_optional(self):
        payload = {
            "name": "Reza",
            "phone": "\u06f0\u06f9\u06f1\u06f2\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7",
            "email": "reza@example.com",
            "message": "Price inquiry",
        }
        response = self.client.post(reverse("core:home"), payload, follow=True)

        self.assertRedirects(response, f"{reverse('core:home')}?lang=en#contact")
        self.assertEqual(Inquiry.objects.count(), 1)
        # Localised digits are normalised before saving
        self.assertEqual(Inquiry.objects.first().phone, "09121234567")

    def test_invalid_phone_is_rejected(self):
        payload = {**VALID_PAYLOAD, "phone": "12"}
        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertContains(response, "Enter a valid phone number.")

    def test_short_message_is_rejected(self):
        payload = {**VALID_PAYLOAD, "message": "Hi"}
        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertContains(response, "Please provide more details.")

    def test_honeypot_blocks_bots(self):
        payload = {**VALID_PAYLOAD, "website": "http://spam.example"}
        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertContains(response, "Invalid request.")

    def test_inquiry_always_emails_customer(self):
        self.client.post(reverse("core:home"), VALID_PAYLOAD)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ali@example.com"])
        self.assertIn("Your inquiry was received", mail.outbox[0].subject)

    @override_settings(CONTACT_NOTIFY_EMAIL="admin@example.com")
    def test_inquiry_emails_customer_and_admin(self):
        self.client.post(reverse("core:home"), VALID_PAYLOAD)

        self.assertEqual(len(mail.outbox), 2)
        admin_mail, customer_mail = mail.outbox
        self.assertEqual(admin_mail.to, ["admin@example.com"])
        self.assertEqual(customer_mail.to, ["ali@example.com"])
        self.assertIn("New inquiry", admin_mail.subject)
        self.assertIn("ali@example.com", admin_mail.body)

    @override_settings(CONTACT_NOTIFY_EMAIL="first@example.com, second@example.com")
    def test_admin_recipients_accept_comma_separated_list(self):
        self.client.post(reverse("core:home"), VALID_PAYLOAD)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].to, ["first@example.com", "second@example.com"]
        )

    def test_email_timeout_is_configured(self):
        self.assertEqual(settings.EMAIL_TIMEOUT, 10)

    def test_invalid_email_is_rejected(self):
        payload = {**VALID_PAYLOAD, "email": "not-an-email"}
        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)

    @override_settings(INQUIRY_RATE_LIMIT=2, INQUIRY_RATE_WINDOW=600)
    def test_rate_limit_blocks_extra_submissions(self):
        for _ in range(2):
            self.client.post(reverse("core:home"), VALID_PAYLOAD)

        response = self.client.post(reverse("core:home"), VALID_PAYLOAD, follow=True)

        self.assertEqual(Inquiry.objects.count(), 2)
        self.assertContains(
            response,
            "Too many inquiries from this device. Please try again in a few minutes.",
        )

    @override_settings(INQUIRY_RATE_LIMIT=1, TRUST_PROXY_HEADERS=True)
    def test_rate_limit_uses_forwarded_ip_only_when_proxy_is_trusted(self):
        first = self.client.post(
            reverse("core:home"),
            VALID_PAYLOAD,
            HTTP_X_FORWARDED_FOR="1.1.1.1, 10.0.0.1",
        )
        second = self.client.post(
            reverse("core:home"),
            VALID_PAYLOAD,
            HTTP_X_FORWARDED_FOR="2.2.2.2, 10.0.0.1",
        )

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Inquiry.objects.count(), 2)

    def test_proxy_headers_are_ignored_by_default(self):
        request = RequestFactory().post(
            "/", REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR="1.1.1.1, 10.0.0.1"
        )
        self.assertEqual(_client_ip(request), "10.0.0.1")

    @override_settings(TRUST_PROXY_HEADERS=True, TRUSTED_PROXY_COUNT=1)
    def test_proxy_headers_are_used_when_explicitly_trusted(self):
        request = RequestFactory().post(
            "/", REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR="1.1.1.1, 10.0.0.1"
        )
        self.assertEqual(_client_ip(request), "1.1.1.1")

    def test_form_errors_keep_contact_anchor(self):
        response = self.client.post(reverse("core:home"), {**VALID_PAYLOAD, "phone": ""})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'action="/?lang=en#contact"')


class ProductTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

    def _sample_image(self, name="nozzle.png"):
        buffer = BytesIO()
        Image.new("RGB", (1200, 900), (205, 160, 70)).save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

    def _create_product(self, **overrides):
        data = {
            "name": "Weft injection nozzle",
            "category": Product.CATEGORY_WEFT,
            "brand": "PICANOL",
            "machine_models": "GTX / GAMMA",
            "summary": "Genuine nozzle for Picanol air-jet machines.",
            "image": self._sample_image(),
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def test_active_product_with_specs_is_rendered(self):
        product = self._create_product()
        product.specs.create(label="Part number", value="PIC-1042-A", sort_order=1)

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weft injection nozzle")
        self.assertContains(response, "PIC-1042-A")
        self.assertContains(response, "product-card")
        self.assertContains(response, 'data-inquire="Weft injection nozzle"')

    def test_inactive_product_is_hidden(self):
        self._create_product(is_active=False)

        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, "Weft injection nozzle")

    def test_thumbnail_is_generated_as_webp(self):
        product = self._create_product()

        self.assertTrue(product.image_thumb.name.endswith("-thumb.webp"))
        thumb_path = Path(self.media_root) / product.image_thumb.name
        self.assertTrue(thumb_path.exists())
        with Image.open(thumb_path) as thumb:
            self.assertEqual(thumb.format, "WEBP")
            self.assertLessEqual(max(thumb.size), 960)

    def test_old_files_are_deleted_after_transaction_commit(self):
        product = self._create_product()
        old_image = product.image.name
        old_thumb = product.image_thumb.name

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            product.image = self._sample_image("replacement.png")
            product.save()

        self.assertTrue(callbacks)
        self.assertFalse((Path(self.media_root) / old_image).exists())
        self.assertFalse((Path(self.media_root) / old_thumb).exists())

    def test_failed_thumbnail_generation_clears_old_thumbnail(self):
        product = self._create_product()

        with patch("core.models.make_thumbnail", return_value=None):
            product.image = self._sample_image("broken.png")
            product.save()

        self.assertEqual(product.image_thumb.name, "")

    def test_save_with_update_fields_keeps_thumbnail(self):
        product = self._create_product()
        thumb_name = product.image_thumb.name

        product.name = "New name"
        product.save(update_fields=["name"])
        product.refresh_from_db()

        self.assertEqual(product.name, "New name")
        self.assertEqual(product.image_thumb.name, thumb_name)


class ProductCatalogTests(TestCase):
    def _product(self, name="Test nozzle", **overrides):
        data = {
            "name": name,
            "category": Product.CATEGORY_WEFT,
            "brand": "PICANOL",
            "machine_models": "GTX",
            "summary": "Short description for catalogue test.",
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def test_catalog_page_lists_only_active_products(self):
        self._product(name="Test nozzle")
        self._product(name="Hidden part", is_active=False)

        response = self.client.get(reverse("core:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All spare parts")
        self.assertContains(response, "Test nozzle")
        self.assertNotContains(response, "Hidden part")

    def test_home_page_links_to_full_catalog(self):
        self._product()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, reverse("core:product_list"))

    def test_catalog_search_matches_name_brand_and_machine(self):
        self._product(name="Picanol nozzle", brand="PICANOL", machine_models="GTX")
        self._product(name="Dornier belt", brand="DORNIER", machine_models="HTV")

        response = self.client.get(reverse("core:product_list"), {"q": "Dornier"})

        self.assertContains(response, "Dornier belt")
        self.assertNotContains(response, "Picanol nozzle")

        response = self.client.get(reverse("core:product_list"), {"q": "GTX"})

        self.assertContains(response, "Picanol nozzle")
        self.assertNotContains(response, "Dornier belt")

    def test_catalog_filters_by_category_and_brand(self):
        self._product(
            name="Weft nozzle",
            category=Product.CATEGORY_WEFT,
            brand="PICANOL",
        )
        self._product(
            name="Electronic board",
            category=Product.CATEGORY_ELECTRONIC,
            brand="DORNIER",
        )

        response = self.client.get(
            reverse("core:product_list"),
            {"category": Product.CATEGORY_ELECTRONIC, "brand": "DORNIER"},
        )

        self.assertContains(response, "Electronic board")
        self.assertNotContains(response, "Weft nozzle")

    def test_unknown_filter_values_are_ignored(self):
        self._product(name="Weft nozzle")
        self._product(name="Electronic board", category=Product.CATEGORY_ELECTRONIC)

        response = self.client.get(
            reverse("core:product_list"),
            {"category": "not-a-category", "brand": "NOT-A-BRAND"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weft nozzle")
        self.assertContains(response, "Electronic board")

    @override_settings(PRODUCTS_PAGE_SIZE=6)
    def test_catalog_pagination_limits_results(self):
        for index in range(13):
            self._product(name=f"Part number {index}")

        response = self.client.get(reverse("core:product_list"))

        self.assertEqual(len(response.context["products"]), 6)
        self.assertContains(response, "page=2")

        second = self.client.get(reverse("core:product_list"), {"page": 2})

        self.assertEqual(second.status_code, 200)
        self.assertEqual(len(second.context["products"]), 6)

    def test_detail_page_shows_specs_and_inquiry_link(self):
        product = self._product()
        product.specs.create(label="Part number", value="PIC-999", sort_order=1)

        response = self.client.get(product.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PIC-999")
        self.assertContains(response, "Request a quote for this part")
        self.assertContains(
            response, f"?product={product.pk}&amp;lang=en#contact"
        )

    def test_inactive_product_detail_returns_404(self):
        product = self._product(is_active=False)

        response = self.client.get(product.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_home_prefills_inquiry_from_product_link(self):
        product = self._product()

        response = self.client.get(reverse("core:home"), {"product": product.pk})

        self.assertContains(response, f"Price inquiry for: {product.name}")

    def test_very_long_product_parameter_does_not_crash(self):
        response = self.client.get(reverse("core:home"), {"product": "9" * 5000})

        self.assertEqual(response.status_code, 200)

    def test_non_numeric_product_parameter_is_ignored(self):
        response = self.client.get(reverse("core:home"), {"product": "not-a-number"})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'value="Price inquiry for:')

    @override_settings(PRODUCTS_HOME_LIMIT=2)
    def test_home_limits_products_and_shows_total(self):
        for index in range(4):
            self._product(name=f"Home page part {index}")

        response = self.client.get(reverse("core:home"))

        self.assertEqual(len(response.context["products"]), 2)
        self.assertContains(response, "View all products (4 parts)")

    def test_home_fragment_links_have_targets(self):
        response = self.client.get(reverse("core:home"))
        html = response.content.decode()
        ids = set(re.findall(r'id="([^"]+)"', html))
        fragments = set(re.findall(r'href="#([^"]+)"', html))

        self.assertTrue({"home", "about", "products", "brands", "club", "contact"} <= ids)
        self.assertFalse(fragments - ids, fragments - ids)


class LanguageTests(TestCase):
    def test_english_is_default_and_ltr(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, '<html lang="en" dir="ltr"', status_code=200)
        self.assertContains(response, "Weaving machine spare parts")

    def test_english_is_available_explicitly(self):
        response = self.client.get(reverse("core:home"), {"lang": "en"})

        self.assertEqual(response["Content-Language"], "en")
        self.assertContains(response, '<html lang="en" dir="ltr"', status_code=200)
        self.assertContains(response, "Browse part categories")
        self.assertContains(response, "Request a quote")
        self.assertNotContains(response, "Mitgliedschaft beantragen")

    def test_german_translation_and_ltr(self):
        response = self.client.get(reverse("core:home"), {"lang": "de"})

        self.assertEqual(response["Content-Language"], "de")
        self.assertContains(response, '<html lang="de" dir="ltr"', status_code=200)
        self.assertContains(response, "Angebot anfragen")
        self.assertContains(response, "Ersatzteile")
        self.assertContains(response, "Seit 2006 beliefern wir")
        self.assertNotContains(response, "{since}")

    def test_catalog_is_translated(self):
        response = self.client.get(reverse("core:product_list"), {"lang": "de"})

        self.assertContains(response, "Alle Ersatzteile")
        self.assertContains(response, "Teilekatalog")

    def test_language_cookie_is_remembered(self):
        first = self.client.get(reverse("core:home"), {"lang": "de"})
        self.assertEqual(first.cookies["parsstore_lang"].value, "de")

        second = self.client.get(reverse("core:home"))
        self.assertContains(second, "Angebot anfragen")

    def test_unsupported_language_falls_back_to_english(self):
        response = self.client.get(reverse("core:home"), {"lang": "xx"})

        self.assertEqual(response["Content-Language"], "en")
        self.assertContains(response, 'dir="ltr"')

    def test_switch_links_keep_current_filters(self):
        response = self.client.get(
            reverse("core:product_list"), {"q": "nozzle"}
        )

        self.assertContains(response, "/products/?lang=en&amp;q=nozzle")
        self.assertContains(response, "/products/?lang=de&amp;q=nozzle")

    def test_form_labels_follow_language(self):
        response = self.client.get(reverse("core:home"), {"lang": "de"})

        self.assertContains(response, "Vollständiger Name")
        self.assertContains(response, "E-Mail-Adresse")
        self.assertContains(response, "Webmaschinenmodell")

    def test_inquiry_confirmation_email_follows_language(self):
        payload = {**VALID_PAYLOAD, "email": "ali@example.com"}
        self.client.post(reverse("core:home") + "?lang=de", payload)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Ihre Anfrage ist eingegangen", mail.outbox[0].body)


class ClubTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_club_section_and_form_are_rendered(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Customer club")
        self.assertContains(response, 'name="form_type" value="club"')

    def test_signup_creates_pending_member(self):
        response = self.client.post(reverse("core:home"), CLUB_PAYLOAD, follow=True)

        self.assertRedirects(response, f"{reverse('core:home')}?lang=en#club")
        self.assertEqual(Customer.objects.count(), 1)

        customer = Customer.objects.first()
        self.assertEqual(customer.full_name, "Maryam Ahmadi")
        self.assertEqual(customer.phone, "09121234567")
        self.assertEqual(customer.email, "maryam@example.com")
        self.assertEqual(customer.status, Customer.STATUS_PENDING)
        self.assertEqual(customer.discount_percent, 5)
        self.assertTrue(customer.code.startswith("PT-"))
        self.assertContains(response, "Your membership request was received.")

    def test_phone_separators_and_localised_digits_are_normalized(self):
        payload = {**CLUB_PAYLOAD, "phone": "\u06f0\u06f9\u06f1\u06f2-\u06f1\u06f2\u06f3-\u06f4\u06f5\u06f6\u06f7"}

        self.client.post(reverse("core:home"), payload)

        self.assertEqual(Customer.objects.first().phone, "09121234567")

    def test_duplicate_phone_is_rejected(self):
        Customer.objects.create(
            first_name="Maryam",
            last_name="Ahmadi",
            phone="09121234567",
            email="maryam@example.com",
        )

        response = self.client.post(
            reverse("core:home"), {**CLUB_PAYLOAD, "phone": "\u06f0\u06f9\u06f1\u06f2-\u06f1\u06f2\u06f3-\u06f4\u06f5\u06f6\u06f7"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertContains(response, "already registered")

    def test_honeypot_blocks_bots(self):
        payload = {**CLUB_PAYLOAD, "website": "http://spam.example"}

        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.count(), 0)
        self.assertContains(response, "Invalid request.")

    def test_signup_always_emails_customer(self):
        self.client.post(reverse("core:home"), CLUB_PAYLOAD)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["maryam@example.com"])
        self.assertIn("club membership request", mail.outbox[0].subject)

    @override_settings(CLUB_NOTIFY_EMAIL="club-admin@example.com")
    def test_signup_emails_customer_and_admin(self):
        self.client.post(reverse("core:home"), CLUB_PAYLOAD)

        self.assertEqual(len(mail.outbox), 2)
        admin_mail, customer_mail = mail.outbox
        self.assertEqual(admin_mail.to, ["club-admin@example.com"])
        self.assertEqual(customer_mail.to, ["maryam@example.com"])
        self.assertIn("Club membership request", admin_mail.subject)
        self.assertIn("maryam@example.com", admin_mail.body)

    @override_settings(CONTACT_NOTIFY_EMAIL="owner@example.com", CLUB_NOTIFY_EMAIL="")
    def test_signup_admin_email_falls_back_to_contact_recipient(self):
        self.client.post(reverse("core:home"), CLUB_PAYLOAD)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])

    @override_settings(CLUB_RATE_LIMIT=1, CLUB_RATE_WINDOW=3600)
    def test_rate_limit_blocks_extra_signups(self):
        self.client.post(reverse("core:home"), CLUB_PAYLOAD)

        response = self.client.post(reverse("core:home"), CLUB_PAYLOAD, follow=True)

        self.assertEqual(Customer.objects.count(), 1)
        self.assertContains(
            response,
            "Too many membership requests from this device. Please try again later.",
        )


class AdminActionTests(TestCase):
    def test_activate_action_updates_timestamp(self):
        user = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "strong-pass-123"
        )
        self.client.force_login(user)
        customer = Customer.objects.create(
            first_name="Maryam",
            last_name="Ahmadi",
            phone="09121234567",
            email="maryam@example.com",
        )

        self.client.post(
            reverse("admin:core_customer_changelist"),
            {"action": "activate_members", "_selected_action": [str(customer.pk)]},
            follow=True,
        )

        customer.refresh_from_db()
        self.assertEqual(customer.status, Customer.STATUS_ACTIVE)
        self.assertGreater(customer.updated_at, customer.created_at)


class ErrorPageTests(TestCase):
    def test_unknown_page_returns_404(self):
        response = self.client.get("/this-page-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)

    def test_404_page_is_translated(self):
        response = self.client.get("/this-page-does-not-exist/?lang=de")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Seite nicht gefunden", status_code=404)
