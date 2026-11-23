"""Create optimised WebP thumbnails for product images.

The full-resolution original is kept, while a smaller version (at most 960x960)
is generated for home-page cards. Instead of downloading a multi-megabyte
file, the browser receives a lightweight image and the page loads quickly.
"""

from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

THUMB_MAX_SIZE = (960, 960)
THUMB_QUALITY = 82


def make_thumbnail(image_field) -> ContentFile | None:
    """Build an optimised WebP from an uploaded image; return ``None`` on error."""
    if not image_field:
        return None

    try:
        image_field.open("rb")
        with Image.open(image_field) as source:
            image = ImageOps.exif_transpose(source)

            # Transparent images are flattened onto white so the WebP is saved
            # without an alpha channel and stays smaller.
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
