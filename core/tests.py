import shutil
import tempfile
from io import BytesIO
from pathlib import Path

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Customer, Inquiry, Product

VALID_PAYLOAD = {
    "name": "علی رضایی",
    "company": "نساجی البرز",
    "phone": "09121234567",
    "email": "ali@example.com",
    "machine": "Picanol GTX",
    "message": "یک عدد نوزل نیاز دارم.",
}


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "پارس تکستایل")
        self.assertContains(response, "PICANOL")

    def test_home_page_has_security_headers(self):
        response = self.client.get(reverse("core:home"))

        self.assertIn("Content-Security-Policy", response)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertIn("camera=()", response["Permissions-Policy"])
        # هیچ منبع خارجی در CSP مجاز نیست
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


class InquiryFormTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_inquiry_form_saves_request(self):
        response = self.client.post(reverse("core:home"), VALID_PAYLOAD, follow=True)

        self.assertRedirects(response, f"{reverse('core:home')}#contact")
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertContains(response, "استعلام شما ثبت شد")

        inquiry = Inquiry.objects.first()
        self.assertEqual(inquiry.name, "علی رضایی")
        self.assertEqual(inquiry.phone, "09121234567")
        self.assertEqual(inquiry.email, "ali@example.com")

    def test_company_and_machine_are_optional(self):
        payload = {
            "name": "رضا",
            "phone": "۰۹۱۲۱۲۳۴۵۶۷",
            "email": "reza@example.com",
            "message": "استعلام قیمت",
        }
        response = self.client.post(reverse("core:home"), payload, follow=True)

        self.assertRedirects(response, f"{reverse('core:home')}#contact")
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_invalid_phone_is_rejected(self):
        payload = {**VALID_PAYLOAD, "phone": "12"}
        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertContains(response, "شماره تماس معتبر وارد کنید")

    def test_short_message_is_rejected(self):
        payload = {**VALID_PAYLOAD, "message": "سلام"}
        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertContains(response, "توضیحات را کامل‌تر بنویسید")

    def test_honeypot_blocks_bots(self):
        payload = {**VALID_PAYLOAD, "website": "http://spam.example"}
        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertContains(response, "درخواست نامعتبر است")

    def test_inquiry_always_emails_customer(self):
        self.client.post(reverse("core:home"), VALID_PAYLOAD)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ali@example.com"])
        self.assertIn("استعلام شما", mail.outbox[0].subject)

    @override_settings(CONTACT_NOTIFY_EMAIL="admin@example.com")
    def test_inquiry_emails_customer_and_admin(self):
        self.client.post(reverse("core:home"), VALID_PAYLOAD)

        self.assertEqual(len(mail.outbox), 2)
        admin_mail, customer_mail = mail.outbox
        self.assertEqual(admin_mail.to, ["admin@example.com"])
        self.assertEqual(customer_mail.to, ["ali@example.com"])
        self.assertIn("استعلام جدید", admin_mail.subject)
        self.assertIn("ali@example.com", admin_mail.body)

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
        self.assertContains(response, "تعداد استعلام‌های ارسالی از این دستگاه زیاد است")


class ProductTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

    def _sample_image(self):
        buffer = BytesIO()
        Image.new("RGB", (1200, 900), (205, 160, 70)).save(buffer, format="PNG")
        return SimpleUploadedFile(
            "nozzle.png", buffer.getvalue(), content_type="image/png"
        )

    def _create_product(self, **overrides):
        data = {
            "name": "نوزل تزریق وفت",
            "category": Product.CATEGORY_WEFT,
            "brand": "PICANOL",
            "machine_models": "GTX / GAMMA",
            "summary": "نوزل اصلی برای ماشین‌های ایرجت پیکانول.",
            "image": self._sample_image(),
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def test_active_product_with_specs_is_rendered(self):
        product = self._create_product()
        product.specs.create(label="شماره فنی", value="PIC-1042-A", sort_order=1)

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "نوزل تزریق وفت")
        self.assertContains(response, "PIC-1042-A")
        self.assertContains(response, "product-card")
        self.assertContains(response, 'data-inquire="نوزل تزریق وفت"')

    def test_inactive_product_is_hidden(self):
        self._create_product(is_active=False)

        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, "نوزل تزریق وفت")

    def test_thumbnail_is_generated_as_webp(self):
        product = self._create_product()

        self.assertTrue(product.image_thumb.name.endswith("-thumb.webp"))
        thumb_path = Path(self.media_root) / product.image_thumb.name
        self.assertTrue(thumb_path.exists())
        with Image.open(thumb_path) as thumb:
            self.assertEqual(thumb.format, "WEBP")
            self.assertLessEqual(max(thumb.size), 960)


class ProductCatalogTests(TestCase):
    def _product(self, name="نوزل تست", **overrides):
        data = {
            "name": name,
            "category": Product.CATEGORY_WEFT,
            "brand": "PICANOL",
            "machine_models": "GTX",
            "summary": "توضیح کوتاه برای تست کاتالوگ.",
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def test_catalog_page_lists_only_active_products(self):
        self._product(name="نوزل تست")
        self._product(name="قطعهٔ مخفی", is_active=False)

        response = self.client.get(reverse("core:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "همهٔ قطعات یدکی")
        self.assertContains(response, "نوزل تست")
        self.assertNotContains(response, "قطعهٔ مخفی")

    def test_home_page_links_to_full_catalog(self):
        self._product()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, reverse("core:product_list"))

    def test_catalog_search_matches_name_brand_and_machine(self):
        self._product(name="نوزل پیکانول", brand="PICANOL", machine_models="GTX")
        self._product(name="تسمه دورنیه", brand="DORNIER", machine_models="HTV")

        response = self.client.get(reverse("core:product_list"), {"q": "دورنیه"})

        self.assertContains(response, "تسمه دورنیه")
        self.assertNotContains(response, "نوزل پیکانول")

        response = self.client.get(reverse("core:product_list"), {"q": "GTX"})

        self.assertContains(response, "نوزل پیکانول")
        self.assertNotContains(response, "تسمه دورنیه")

    def test_catalog_filters_by_category_and_brand(self):
        self._product(
            name="نوزل وفت",
            category=Product.CATEGORY_WEFT,
            brand="PICANOL",
        )
        self._product(
            name="برد الکترونیکی",
            category=Product.CATEGORY_ELECTRONIC,
            brand="DORNIER",
        )

        response = self.client.get(
            reverse("core:product_list"),
            {"category": Product.CATEGORY_ELECTRONIC, "brand": "DORNIER"},
        )

        self.assertContains(response, "برد الکترونیکی")
        self.assertNotContains(response, "نوزل وفت")

    def test_unknown_filter_values_are_ignored(self):
        self._product(name="نوزل وفت")
        self._product(name="برد الکترونیکی", category=Product.CATEGORY_ELECTRONIC)

        response = self.client.get(
            reverse("core:product_list"),
            {"category": "not-a-category", "brand": "NOT-A-BRAND"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "نوزل وفت")
        self.assertContains(response, "برد الکترونیکی")

    @override_settings(PRODUCTS_PAGE_SIZE=6)
    def test_catalog_pagination_limits_results(self):
        for index in range(13):
            self._product(name=f"قطعهٔ شمارهٔ {index}")

        response = self.client.get(reverse("core:product_list"))

        self.assertEqual(len(response.context["products"]), 6)
        self.assertContains(response, "page=2")

        second = self.client.get(reverse("core:product_list"), {"page": 2})

        self.assertEqual(second.status_code, 200)
        self.assertEqual(len(second.context["products"]), 6)

    def test_detail_page_shows_specs_and_inquiry_link(self):
        product = self._product()
        product.specs.create(label="شماره فنی", value="PIC-999", sort_order=1)

        response = self.client.get(product.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PIC-999")
        self.assertContains(response, "استعلام قیمت این قطعه")
        self.assertContains(response, f"?product={product.pk}#contact")

    def test_inactive_product_detail_returns_404(self):
        product = self._product(is_active=False)

        response = self.client.get(product.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_home_prefills_inquiry_from_product_link(self):
        product = self._product()

        response = self.client.get(reverse("core:home"), {"product": product.pk})

        self.assertContains(response, f"استعلام قیمت برای: {product.name}")

    @override_settings(PRODUCTS_HOME_LIMIT=2)
    def test_home_limits_products_and_shows_total(self):
        for index in range(4):
            self._product(name=f"قطعهٔ صفحهٔ اصلی {index}")

        response = self.client.get(reverse("core:home"))

        self.assertEqual(len(response.context["products"]), 2)
        self.assertContains(response, "مشاهده همهٔ محصولات (4 قطعه)")


class ClubTests(TestCase):
    payload = {
        "form_type": "club",
        "first_name": "مریم",
        "last_name": "احمدی",
        "company": "نساجی البرز",
        "phone": "۰۹۱۲۱۲۳۴۵۶۷",
        "email": "maryam@example.com",
    }

    def setUp(self):
        cache.clear()

    def test_club_section_and_form_are_rendered(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "باشگاه مشتریان")
        self.assertContains(response, 'name="form_type" value="club"')

    def test_signup_creates_pending_member(self):
        response = self.client.post(reverse("core:home"), self.payload, follow=True)

        self.assertRedirects(response, f"{reverse('core:home')}#club")
        self.assertEqual(Customer.objects.count(), 1)

        customer = Customer.objects.first()
        self.assertEqual(customer.full_name, "مریم احمدی")
        self.assertEqual(customer.phone, "09121234567")
        self.assertEqual(customer.email, "maryam@example.com")
        self.assertEqual(customer.status, Customer.STATUS_PENDING)
        self.assertEqual(customer.discount_percent, 5)
        self.assertTrue(customer.code.startswith("PT-"))
        self.assertContains(response, "درخواست عضویت شما ثبت شد")

    def test_duplicate_phone_is_rejected(self):
        Customer.objects.create(
            first_name="مریم",
            last_name="احمدی",
            phone="09121234567",
            email="maryam@example.com",
        )

        response = self.client.post(reverse("core:home"), self.payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertContains(response, "قبلاً در باشگاه مشتریان ثبت شده است")

    def test_honeypot_blocks_bots(self):
        payload = {**self.payload, "website": "http://spam.example"}

        response = self.client.post(reverse("core:home"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.count(), 0)
        self.assertContains(response, "درخواست نامعتبر است")

    def test_signup_always_emails_customer(self):
        self.client.post(reverse("core:home"), self.payload)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["maryam@example.com"])
        self.assertIn("باشگاه مشتریان", mail.outbox[0].subject)

    @override_settings(CLUB_NOTIFY_EMAIL="club-admin@example.com")
    def test_signup_emails_customer_and_admin(self):
        self.client.post(reverse("core:home"), self.payload)

        self.assertEqual(len(mail.outbox), 2)
        admin_mail, customer_mail = mail.outbox
        self.assertEqual(admin_mail.to, ["club-admin@example.com"])
        self.assertEqual(customer_mail.to, ["maryam@example.com"])
        self.assertIn("عضویت باشگاه", admin_mail.subject)
        self.assertIn("maryam@example.com", admin_mail.body)

    @override_settings(CONTACT_NOTIFY_EMAIL="owner@example.com", CLUB_NOTIFY_EMAIL="")
    def test_signup_admin_email_falls_back_to_contact_recipient(self):
        self.client.post(reverse("core:home"), self.payload)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])

    @override_settings(CLUB_RATE_LIMIT=1, CLUB_RATE_WINDOW=3600)
    def test_rate_limit_blocks_extra_signups(self):
        self.client.post(reverse("core:home"), self.payload)

        response = self.client.post(reverse("core:home"), self.payload, follow=True)

        self.assertEqual(Customer.objects.count(), 1)
        self.assertContains(response, "تعداد درخواست‌های عضویت از این دستگاه زیاد است")


class ErrorPageTests(TestCase):
    def test_unknown_page_returns_404(self):
        response = self.client.get("/this-page-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "این صفحه پیدا نشد", status_code=404)
