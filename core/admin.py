from pathlib import Path

from django.contrib import admin, messages
from django.utils.html import format_html

from .images import make_thumbnail
from .models import Customer, Inquiry, Product, ProductSpec


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "phone", "machine", "is_processed", "created_at")
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "company", "phone", "machine", "message")
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
    fieldsets = (
        (
            "اطلاعات محصول",
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
            "تصویر",
            {
                "fields": ("image", "thumbnail_preview", "image_alt"),
                "description": (
                    "تصویر اصلی را یک‌بار آپلود کنید؛ نسخهٔ WebP بهینه خودکار ساخته "
                    "می‌شود و در صفحهٔ اصلی همان نمایش داده می‌شود. نسبت پیشنهادی ۴:۳."
                ),
            },
        ),
        (
            "نمایش در سایت",
            {"fields": ("is_featured", "is_active", "sort_order")},
        ),
        (
            "زمان‌ها",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="پیش‌نمایش تصویر")
    def thumbnail_preview(self, obj):
        image = obj.display_image
        if not image:
            return "تصویری آپلود نشده است."
        return format_html(
            '<img src="{}" alt="" width="180" height="135">', image.url
        )

    @admin.action(description="بازسازی بندانگشتی WebP")
    def rebuild_thumbnails(self, request, queryset):
        rebuilt = 0
        for product in queryset:
            if not product.image:
                continue
            content = make_thumbnail(product.image)
            if content is None:
                continue
            product.image_thumb.save(
                f"{Path(product.image.name).stem}-thumb.webp", content, save=False
            )
            product.save(update_fields=["image_thumb"])
            rebuilt += 1
        self.message_user(
            request,
            f"بندانگشتی {rebuilt} محصول بازسازی شد.",
            messages.SUCCESS,
        )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "first_name",
        "last_name",
        "phone",
        "company",
        "tier",
        "discount_percent",
        "status",
        "created_at",
    )
    list_filter = ("status", "tier", "created_at")
    search_fields = ("code", "first_name", "last_name", "phone", "company")
    list_editable = ("tier", "discount_percent", "status")
    readonly_fields = ("code", "created_at", "updated_at")
    actions = ("activate_members", "block_members")
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "هویت عضو",
            {"fields": ("code", "first_name", "last_name", "phone", "company")},
        ),
        (
            "باشگاه",
            {
                "fields": ("tier", "discount_percent", "status", "notes"),
                "description": (
                    "درصد تخفیف همان مقداری است که هنگام خرید روی پیش‌فاکتور "
                    "اعمال می‌شود؛ سطح عضویت فقط برای دسته‌بندی مشتریان است."
                ),
            },
        ),
        (
            "زمان‌ها",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.action(description="فعال‌سازی عضویت‌های انتخاب‌شده")
    def activate_members(self, request, queryset):
        updated = queryset.update(status=Customer.STATUS_ACTIVE)
        self.message_user(
            request, f"{updated} عضویت فعال شد.", messages.SUCCESS
        )

    @admin.action(description="مسدودسازی عضویت‌های انتخاب‌شده")
    def block_members(self, request, queryset):
        updated = queryset.update(status=Customer.STATUS_BLOCKED)
        self.message_user(
            request, f"{updated} عضویت مسدود شد.", messages.WARNING
        )
