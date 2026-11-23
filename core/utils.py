"""Shared helpers for cleaning user input."""

# Non-Latin digits are mapped to Latin so numbers are stored consistently.
_DIGIT_MAP = str.maketrans(
    "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669",
    "01234567890123456789",
)


def normalize_digits(value: str) -> str:
    """Convert localised digits to Latin digits."""
    return (value or "").translate(_DIGIT_MAP)


def phone_digits(value: str) -> str:
    """Return only Latin digits from a phone number."""
    return "".join(ch for ch in normalize_digits(value) if ch.isdigit())
