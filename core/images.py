"""ساخت بندانگشتی WebP برای تصاویر محصولات.

تصویر اصلی با کیفیت کامل نگهداری می‌شود و نسخهٔ کوچک‌تر (حداکثر ۹۶۰×۹۶۰)
برای کارت‌های صفحهٔ اصلی ساخته می‌شود؛ به این ترتیب مرورگر به‌جای فایل
چند مگابایتی، یک فایل سبک دریافت می‌کند و صفحه سریع باز می‌شود.
"""

from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

THUMB_MAX_SIZE = (960, 960)
THUMB_QUALITY = 82


def make_thumbnail(image_field) -> ContentFile | None:
    """تبدیل تصویر آپلودشده به WebP بهینه؛ در صورت خطا ``None`` برمی‌گردد."""
    if not image_field:
        return None

    try:
        image_field.open("rb")
        with Image.open(image_field) as source:
            image = ImageOps.exif_transpose(source)

            # تصاویر دارای شفافیت روی پس‌زمینهٔ سفید تخت می‌شوند تا WebP بدون
            # کانال آلفا و با حجم کمتر ذخیره شود.
            if image.mode in {"RGBA", "LA", "P"}:
                image = image.convert("RGBA")
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            else:
                image = image.convert("RGB")

            image.thumbnail(THUMB_MAX_SIZE, Image.Resampling.LANCZOS)
            buffer = BytesIO()
            image.save(buffer, format="WEBP", quality=THUMB_QUALITY, method=6)
    except (OSError, ValueError):
        return None
    finally:
        try:
            image_field.seek(0)
        except (OSError, ValueError):
            pass

    return ContentFile(buffer.getvalue())
