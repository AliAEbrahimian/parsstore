"""مدل‌های پایگاه‌دادهٔ پارس تکستایل."""

import secrets
import uuid
from pathlib import Path

from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse

from .images import make_thumbnail
from .utils import normalize_digits


class Inquiry(models.Model):
    """درخواست استعلام قیمت ثبت‌شده از فرم تماس سایت."""

    name = models.CharField("نام و نام خانوادگی", max_length=120)
    company = models.CharField("نام شرکت / کارگاه", max_length=160, blank=True)
    phone = models.CharField("تلفن تماس", max_length=30)
    email = models.EmailField("آدرس ایمیل", max_length=254, default="")
    machine = models.CharField("مدل ماشین بافندگی", max_length=120, blank=True)
    message = models.TextField("توضیحات و قطعات مورد نیاز")
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    is_processed = models.BooleanField("بررسی شده", default=False)

    class Meta:
        verbose_name = "درخواست استعلام"
        verbose_name_plural = "درخواست‌های استعلام"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.phone}"


class Product(models.Model):
    """محصول نمایشی سایت؛ بدون سبد خرید و پرداخت آنلاین."""

    CATEGORY_MECHANICAL = "mechanical"
    CATEGORY_ELECTRONIC = "electronic"
    CATEGORY_WEFT = "weft"
    CATEGORY_DRIVE = "drive"
    CATEGORY_WEAVING = "weaving"
    CATEGORY_TOOLS = "tools"

    CATEGORY_CHOICES = [
        (CATEGORY_MECHANICAL, "قطعات مکانیکی و سایشی"),
        (CATEGORY_ELECTRONIC, "قطعات الکترونیکی و بردها"),
        (CATEGORY_WEFT, "سیستم وفت، نوزل و پمپ"),
        (CATEGORY_DRIVE, "تسمه، موتور و گیربکس"),
        (CATEGORY_WEAVING, "قطعات بافندگی و مصرفی"),
        (CATEGORY_TOOLS, "ابزار و لوازم فنی"),
    ]

    name = models.CharField("نام محصول", max_length=160)
    brand = models.CharField("برند", max_length=80, blank=True)
    machine_models = models.CharField(
        "مدل ماشین‌های سازگار",
        max_length=200,
        blank=True,
        help_text="مثلاً: GTX / GAMMA / OMNIplus",
    )
    category = models.CharField(
        "دسته‌بندی", max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_MECHANICAL
    )
    summary = models.CharField("توضیح کوتاه", max_length=240)
    description = models.TextField("توضیحات کامل", blank=True)

    image = models.ImageField(
        "تصویر محصول",
        upload_to="products/%Y/%m/",
        blank=True,
        help_text="ترجیحاً WebP یا JPEG، حداکثر ۱۲۰۰×۹۰۰ پیکسل و کمتر از ۴۰۰ کیلوبایت.",
    )
    # نسخهٔ بهینهٔ ۹۶۰ پیکسلی که خودکار از تصویر اصلی ساخته می‌شود.
    image_thumb = models.ImageField(
        "بندانگشتی", upload_to="products/thumbs/%Y/%m/", blank=True, editable=False
    )
    image_alt = models.CharField(
        "متن جایگزین تصویر",
        max_length=180,
        blank=True,
        help_text="در صورت خالی بودن، نام محصول استفاده می‌شود.",
    )

    is_featured = models.BooleanField("محصول منتخب", default=False)
    is_active = models.BooleanField("نمایش در سایت", default=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب نمایش", default=0)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["sort_order", "name"]
        # برای کاتالوگ بزرگ (۸۰۰ تا ۱۲۰۰ قطعه) فیلتر و مرتب‌سازی صفحهٔ محصولات
        # باید از ایندکس استفاده کند تا با رشد کاتالوگ کند نشود.
        indexes = [
            models.Index(
                fields=["is_active", "is_featured", "sort_order"],
                name="product_active_feat_idx",
            ),
            models.Index(fields=["category"], name="product_category_idx"),
            models.Index(fields=["brand"], name="product_brand_idx"),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # برای رکورد تازه، تصویرِ پاس‌داده‌شده «جدید» است و باید بندانگشتی بسازد.
        if self._state.adding:
            self._original_image = ""
            self._original_thumb = ""
        else:
            self._original_image = self.image.name if self.image else ""
            self._original_thumb = self.image_thumb.name if self.image_thumb else ""

    @property
    def display_image(self):
        """بندانگشتی در اولویت است؛ اگر نبود تصویر اصلی نمایش داده می‌شود."""
        return self.image_thumb or self.image

    def get_absolute_url(self) -> str:
        return reverse("core:product_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        image_field = self.image
        image_name = image_field.name if image_field else ""
        # فایل تازه‌آپلودشده _committed=False است؛ حتی اگر نامش با قبلی یکی باشد
        # باید دوباره بندانگشتی ساخته شود.
        image_changed = bool(image_field) and not getattr(
            image_field, "_committed", True
        )
        if not image_changed:
            image_changed = image_name != self._original_image

        if image_changed:
            if self.image:
                content = make_thumbnail(self.image)
                if content is not None:
                    self.image_thumb.save(
                        f"{Path(image_name).stem}-thumb.webp", content, save=False
                    )
                    if kwargs.get("update_fields") is not None:
                        kwargs["update_fields"] = set(kwargs["update_fields"]) | {
                            "image_thumb"
                        }
            else:
                self.image_thumb = ""
                if kwargs.get("update_fields") is not None:
                    kwargs["update_fields"] = set(kwargs["update_fields"]) | {
                        "image_thumb"
                    }

        super().save(*args, **kwargs)

        old_image, old_thumb = self._original_image, self._original_thumb
        self._original_image = self.image.name if self.image else ""
        self._original_thumb = self.image_thumb.name if self.image_thumb else ""

        if image_changed:
            self._delete_file(old_image, keep=self._original_image)
            self._delete_file(old_thumb, keep=self._original_thumb)

    def _delete_file(self, name: str, keep: str = "") -> None:
        """حذف فایل قدیمی پس از جایگزینی تصویر (بدون شکستن ذخیره)."""
        if not name or name == keep:
            return
        try:
            self.image.storage.delete(name)
        except OSError:
            pass

    def __str__(self) -> str:
        return self.name


class ProductSpec(models.Model):
    """یک ردیف مشخصهٔ فنی برای محصول (مثلاً «شماره فنی: PIC-1042-A»)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specs", verbose_name="محصول"
    )
    label = models.CharField("عنوان مشخصه", max_length=60)
    value = models.CharField("مقدار", max_length=120)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "مشخصهٔ فنی"
        verbose_name_plural = "مشخصات فنی"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.label}: {self.value}"


class Customer(models.Model):
    """عضو باشگاه مشتریان؛ تخفیف هنگام خرید حضوری/تلفنی اعمال می‌شود."""

    TIER_BRONZE = "bronze"
    TIER_SILVER = "silver"
    TIER_GOLD = "gold"
    TIER_CHOICES = [
        (TIER_BRONZE, "برنزی"),
        (TIER_SILVER, "نقره‌ای"),
        (TIER_GOLD, "طلایی"),
    ]
    TIER_DISCOUNTS = {TIER_BRONZE: 5, TIER_SILVER: 8, TIER_GOLD: 12}

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_BLOCKED = "blocked"
    STATUS_CHOICES = [
        (STATUS_PENDING, "در انتظار تأیید"),
        (STATUS_ACTIVE, "فعال"),
        (STATUS_BLOCKED, "مسدود"),
    ]

    CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    code = models.CharField(
        "کد عضویت", max_length=12, unique=True, blank=True, editable=False
    )
    first_name = models.CharField("نام", max_length=60)
    last_name = models.CharField("نام خانوادگی", max_length=60)
    company = models.CharField("شرکت / کارگاه", max_length=160, blank=True)
    phone = models.CharField(
        "شماره تماس",
        max_length=20,
        unique=True,
        error_messages={
            "unique": "این شماره قبلاً در باشگاه مشتریان ثبت شده است.",
        },
    )
    email = models.EmailField("آدرس ایمیل", max_length=254, default="")

    tier = models.CharField(
        "سطح عضویت", max_length=10, choices=TIER_CHOICES, default=TIER_BRONZE
    )
    discount_percent = models.PositiveSmallIntegerField(
        "درصد تخفیف",
        default=5,
        validators=[MaxValueValidator(100)],
        help_text="هنگام خرید، همین درصد روی پیش‌فاکتور اعمال می‌شود.",
    )
    status = models.CharField(
        "وضعیت", max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    notes = models.TextField("یادداشت", blank=True)

    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "عضو باشگاه مشتریان"
        verbose_name_plural = "باشگاه مشتریان"
        ordering = ["-created_at"]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_digits(self.phone).strip()
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self) -> str:
        """کد یکتا و خوانا برای اعلام تلفنی هنگام خرید."""
        for _ in range(10):
            candidate = "PT-" + "".join(
                secrets.choice(self.CODE_ALPHABET) for _ in range(6)
            )
            if not Customer.objects.filter(code=candidate).exists():
                return candidate
        return "PT-" + uuid.uuid4().hex[:8].upper()

    def __str__(self) -> str:
        return f"{self.full_name} — {self.phone}"


@receiver(post_delete, sender=Product)
def _delete_product_files(sender, instance, **kwargs):
    """پاک کردن تصویر اصلی و بندانگشتی هنگام حذف محصول."""
    for field in (instance.image, instance.image_thumb):
        if field:
            try:
                field.delete(save=False)
            except OSError:
                pass
