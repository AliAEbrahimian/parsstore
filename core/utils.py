"""کمک‌تابع‌های مشترک برای پاک‌سازی ورودی‌های کاربر."""

# ارقام فارسی و عربی به لاتین نگاشت می‌شوند تا شماره‌ها یکسان ذخیره و مقایسه شوند.
_DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def normalize_digits(value: str) -> str:
    """تبدیل ارقام فارسی/عربی به لاتین."""
    return (value or "").translate(_DIGIT_MAP)


def phone_digits(value: str) -> str:
    """فقط ارقام لاتین شماره تماس را برمی‌گرداند."""
    return "".join(ch for ch in normalize_digits(value) if ch.isdigit())
