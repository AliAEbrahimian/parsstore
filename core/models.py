"""ParsStore database models."""

import secrets
import uuid
from pathlib import Path

from django.core.validators import MaxValueValidator
from django.db import IntegrityError, models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse

from .images import make_thumbnail
from .utils import normalize_digits, phone_digits


class Inquiry(models.Model):
    """A price inquiry submitted through the contact form."""

    name = models.CharField("Full name", max_length=120)
    company = models.CharField("Company / workshop", max_length=160, blank=True)
    phone = models.CharField("Phone", max_length=30)
    email = models.EmailField("Email", max_length=254, default="")
    machine = models.CharField("Machine model", max_length=120, blank=True)
    message = models.TextField("Message")
    created_at = models.DateTimeField("Created", auto_now_add=True)
    is_processed = models.BooleanField("Processed", default=False)

    class Meta:
        verbose_name = "Inquiry"
        verbose_name_plural = "Inquiries"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.phone}"


class Product(models.Model):
    """A showcase product; no shopping cart or online payment."""

    CATEGORY_MECHANICAL = "mechanical"
    CATEGORY_ELECTRONIC = "electronic"
    CATEGORY_WEFT = "weft"
    CATEGORY_DRIVE = "drive"
    CATEGORY_WEAVING = "weaving"
    CATEGORY_TOOLS = "tools"

    CATEGORY_CHOICES = [
        (CATEGORY_MECHANICAL, "Mechanical & wear parts"),
        (CATEGORY_ELECTRONIC, "Electronics & boards"),
        (CATEGORY_WEFT, "Weft, nozzles & pumps"),
        (CATEGORY_DRIVE, "Belts, motors & gearboxes"),
        (CATEGORY_WEAVING, "Weaving & consumables"),
        (CATEGORY_TOOLS, "Tools & technical supplies"),
    ]

    name = models.CharField("Name", max_length=160)
    brand = models.CharField("Brand", max_length=80, blank=True)
    machine_models = models.CharField(
        "Compatible machine models",
        max_length=200,
        blank=True,
        help_text="e.g. GTX / GAMMA / OMNIplus",
    )
    category = models.CharField(
        "Category", max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_MECHANICAL
    )
    summary = models.CharField("Summary", max_length=240)
    description = models.TextField("Description", blank=True)

    image = models.ImageField(
        "Product image",
        upload_to="products/%Y/%m/",
        blank=True,
        help_text="Prefer WebP or JPEG, max 1200×900 px and under 400 KB.",
    )
    image_thumb = models.ImageField(
        "Thumbnail", upload_to="products/thumbs/%Y/%m/", blank=True, editable=False
    )
    image_alt = models.CharField(
        "Image alt text",
        max_length=180,
        blank=True,
        help_text="Defaults to the product name.",
    )

    is_featured = models.BooleanField("Featured", default=False)
    is_active = models.BooleanField("Visible on site", default=True)
    sort_order = models.PositiveSmallIntegerField("Sort order", default=0)
    created_at = models.DateTimeField("Created", auto_now_add=True)
    updated_at = models.DateTimeField("Updated", auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["sort_order", "name"]
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
        if self._state.adding:
            self._original_image = ""
            self._original_thumb = ""
        else:
            # Read file names from field metadata without loading deferred fields
            self._original_image = self.__dict__.get("image") or ""
            self._original_thumb = self.__dict__.get("image_thumb") or ""
            if not self._original_image and self.image:
                self._original_image = self.image.name
            if not self._original_thumb and self.image_thumb:
                self._original_thumb = self.image_thumb.name

    @property
    def display_image(self):
        """Prefer the thumbnail; fall back to the original image."""
        return self.image_thumb or self.image

    def get_absolute_url(self) -> str:
        return reverse("core:product_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        image_field = self.image
        image_name = image_field.name if image_field else ""
        image_changed = bool(image_field) and not getattr(
            image_field, "_committed", True
        )
        if not image_changed:
            image_changed = image_name != self._original_image

        update_fields = kwargs.get("update_fields")
        if image_changed and update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"image", "image_thumb"}

        thumb_failed = False
        if image_changed:
            if self.image:
                content = make_thumbnail(self.image)
                if content is not None:
                    self.image_thumb.save(
                        f"{Path(image_name).stem}-thumb.webp", content, save=False
                    )
                else:
                    # A new image was set but no thumbnail was built; clear the old one
                    thumb_failed = True
                    self.image_thumb = ""
            else:
                self.image_thumb = ""

        super().save(*args, **kwargs)

        old_image, old_thumb = self._original_image, self._original_thumb
        new_image = self.image.name if self.image else ""
        new_thumb = self.image_thumb.name if self.image_thumb else ""

        # Delete files only after the transaction commits; otherwise a database
        # rollback would leave paths pointing at nothing.
        to_delete = []
        if image_changed or thumb_failed:
            if old_image and old_image != new_image:
                to_delete.append(old_image)
            if old_thumb and old_thumb != new_thumb:
                to_delete.append(old_thumb)
        self._delete_files_later(to_delete)

        self._original_image = new_image
        self._original_thumb = new_thumb

    def _delete_files_later(self, names):
        if not names:
            return
        storage = self.image.storage

        def delete_files():
            for name in names:
                try:
                    storage.delete(name)
                except OSError:
                    pass

        transaction.on_commit(delete_files)

    def __str__(self) -> str:
        return self.name


class ProductSpec(models.Model):
    """A single technical specification row for a product."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specs", verbose_name="Product"
    )
    label = models.CharField("Label", max_length=60)
    value = models.CharField("Value", max_length=120)
    sort_order = models.PositiveSmallIntegerField("Sort order", default=0)

    class Meta:
        verbose_name = "Specification"
        verbose_name_plural = "Specifications"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.label}: {self.value}"


class Customer(models.Model):
    """A club member; the discount is applied to in-store/phone purchases."""

    TIER_BRONZE = "bronze"
    TIER_SILVER = "silver"
    TIER_GOLD = "gold"
    TIER_CHOICES = [
        (TIER_BRONZE, "Bronze"),
        (TIER_SILVER, "Silver"),
        (TIER_GOLD, "Gold"),
    ]
    TIER_DISCOUNTS = {TIER_BRONZE: 5, TIER_SILVER: 8, TIER_GOLD: 12}

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_BLOCKED = "blocked"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_BLOCKED, "Blocked"),
    ]

    CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    code = models.CharField(
        "Membership code", max_length=12, unique=True, blank=True, editable=False
    )
    first_name = models.CharField("First name", max_length=60)
    last_name = models.CharField("Last name", max_length=60)
    company = models.CharField("Company / workshop", max_length=160, blank=True)
    phone = models.CharField(
        "Phone",
        max_length=20,
        unique=True,
        error_messages={
            "unique": "This number is already registered in the customer club.",
        },
    )
    email = models.EmailField("Email", max_length=254, default="")

    tier = models.CharField(
        "Tier", max_length=10, choices=TIER_CHOICES, default=TIER_BRONZE
    )
    discount_percent = models.PositiveSmallIntegerField(
        "Discount %",
        default=5,
        validators=[MaxValueValidator(100)],
        help_text="Applied to the proforma invoice at purchase time.",
    )
    status = models.CharField(
        "Status", max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    notes = models.TextField("Notes", blank=True)

    created_at = models.DateTimeField("Created", auto_now_add=True)
    updated_at = models.DateTimeField("Updated", auto_now=True)

    class Meta:
        verbose_name = "Club member"
        verbose_name_plural = "Club members"
        ordering = ["-created_at"]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if self.phone:
            # Strip separators and normalise localised digits before uniqueness check
            self.phone = phone_digits(self.phone)
        if not self.code:
            self.code = self._generate_code()

        for _ in range(10):
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                # Random code collision: generate a new code and retry
                if Customer.objects.filter(code=self.code).exclude(pk=self.pk).exists():
                    self.code = self._generate_code()
                    continue
                raise

    def _generate_code(self) -> str:
        """Generate a unique, readable code for quoting by phone at purchase."""
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
    """Delete the original and thumbnail files after a product is deleted."""
    names = [field.name for field in (instance.image, instance.image_thumb) if field]
    if not names:
        return
    storage = instance.image.storage

    def delete_files():
        for name in names:
            try:
                storage.delete(name)
            except OSError:
                pass

    transaction.on_commit(delete_files)
