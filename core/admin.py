from pathlib import Path

from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from django.utils.html import format_html

from .i18n import t
from .images import make_thumbnail
from .models import Customer, Inquiry, Product, ProductSpec


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "phone",
        "email",
        "machine",
        "is_processed",
        "created_at",
    )
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "company", "phone", "email", "machine", "message")
    list_editable = ("is_processed",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 3
    fields = ("label", "value", "sort_order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "is_featured",
        "is_active",
        "sort_order",
        "updated_at",
    )
    list_filter = ("is_active", "is_featured", "category")
    search_fields = ("name", "brand", "machine_models", "summary", "description")
    list_editable = ("is_featured", "is_active", "sort_order")
    readonly_fields = ("thumbnail_preview", "created_at", "updated_at")
    inlines = (ProductSpecInline,)
    actions = ("rebuild_thumbnails",)
    list_per_page = 50
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Product information",
            {
                "fields": (
                    "name",
                    "category",
                    "brand",
                    "machine_models",
                    "summary",
                    "description",
                )
            },
        ),
        (
            "Image",
            {
                "fields": ("image", "thumbnail_preview", "image_alt"),
                "description": (
                    "Upload the original image once; an optimised WebP version is "
                    "created automatically. Recommended ratio: 4:3."
                ),
            },
        ),
        ("Display", {"fields": ("is_featured", "is_active", "sort_order")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Image preview")
    def thumbnail_preview(self, obj):
        image = obj.display_image
        if not image:
            return "No image uploaded."
        return format_html('<img src="{}" alt="" width="180" height="135">', image.url)

    @admin.action(description="Rebuild WebP thumbnails")
    def rebuild_thumbnails(self, request, queryset):
        rebuilt = 0
        for product in queryset.iterator():
            if not product.image:
                continue
            content = make_thumbnail(product.image)
            if content is None:
                continue
            old_thumb = product.image_thumb.name
            product.image_thumb.save(
                f"{Path(product.image.name).stem}-thumb.webp", content, save=False
            )
            new_thumb = product.image_thumb.name
            product.save(update_fields=["image_thumb", "updated_at"])
            if old_thumb and old_thumb != new_thumb:
                name = old_thumb
                storage = product.image_thumb.storage
                transaction.on_commit(
                    lambda name=name, storage=storage: storage.delete(name)
                )
            rebuilt += 1
        self.message_user(request, t("admin_rebuilt").format(n=rebuilt), messages.SUCCESS)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "first_name",
        "last_name",
        "phone",
        "email",
        "company",
        "tier",
        "discount_percent",
        "status",
        "created_at",
    )
    list_filter = ("status", "tier", "created_at")
    search_fields = ("code", "first_name", "last_name", "phone", "email", "company")
    list_editable = ("tier", "discount_percent", "status")
    readonly_fields = ("code", "created_at", "updated_at")
    actions = ("activate_members", "block_members")
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Member identity",
            {"fields": ("code", "first_name", "last_name", "phone", "email", "company")},
        ),
        (
            "Club",
            {
                "fields": ("tier", "discount_percent", "status", "notes"),
                "description": (
                    "The discount percentage is applied to the proforma invoice at "
                    "purchase time; the tier is only for customer grouping."
                ),
            },
        ),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.action(description="Activate selected memberships")
    def activate_members(self, request, queryset):
        updated = queryset.update(status=Customer.STATUS_ACTIVE, updated_at=timezone.now())
        self.message_user(request, t("admin_activated").format(n=updated), messages.SUCCESS)

    @admin.action(description="Block selected memberships")
    def block_members(self, request, queryset):
        updated = queryset.update(status=Customer.STATUS_BLOCKED, updated_at=timezone.now())
        self.message_user(request, t("admin_blocked").format(n=updated), messages.WARNING)
