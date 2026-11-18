import shutil
import tempfile
from io import BytesIO
from pathlib import Path

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

    def test_company_and_machine_are_optional(self):
        payload = {"name": "رضا", "phone": "۰۹۱۲۱۲۳۴۵۶۷", "message": "استعلام قیمت"}
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


class ClubTests(TestCase):
    payload = {
        "form_type": "club",
        "first_name": "مریم",
        "last_name": "احمدی",
        "company": "نساجی البرز",
        "phone": "۰۹۱۲۱۲۳۴۵۶۷",
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
        self.assertEqual(customer.status, Customer.STATUS_PENDING)
        self.assertEqual(customer.discount_percent, 5)
        self.assertTrue(customer.code.startswith("PT-"))
        self.assertContains(response, "درخواست عضویت شما ثبت شد")

    def test_duplicate_phone_is_rejected(self):
        Customer.objects.create(
            first_name="مریم", last_name="احمدی", phone="09121234567"
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
