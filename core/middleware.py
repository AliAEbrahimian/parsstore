"""هدرهای امنیتی تکمیلی که جنگو به‌صورت پیش‌فرض ارسال نمی‌کند."""

from django.conf import settings


class SecurityHeadersMiddleware:
    """
    افزودن CSP و Permissions-Policy به همه‌ی پاسخ‌ها.

    نکته: این پروژه هیچ منبع خارجی (CDN، فونت آنلاین، اسکریپت تبلیغاتی) ندارد؛
    بنابراین CSP کاملاً سخت‌گیرانه تنظیم شده است.
    """

    CSP = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "script-src 'self'; "
        "style-src 'self'"
    )

    PERMISSIONS_POLICY = (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        headers = {
            "Content-Security-Policy": getattr(settings, "CONTENT_SECURITY_POLICY", self.CSP),
            "Permissions-Policy": self.PERMISSIONS_POLICY,
            "Referrer-Policy": getattr(settings, "SECURE_REFERRER_POLICY", "same-origin"),
            "X-Content-Type-Options": "nosniff",
        }
        for name, value in headers.items():
            if name not in response:
                response[name] = value

        return response
