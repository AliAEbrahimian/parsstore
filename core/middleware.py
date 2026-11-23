"""Security headers and language selection."""

from django.conf import settings
from django.utils import translation

from .i18n import DEFAULT_LANGUAGE, LANGUAGES


class SecurityHeadersMiddleware:
    """Add CSP and Permissions-Policy headers to every response."""

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
        response.setdefault("Content-Security-Policy", self.CSP)
        response.setdefault("Permissions-Policy", self.PERMISSIONS_POLICY)
        return response


class LanguageMiddleware:
    """Determine the language from ``?lang=`` / cookie and store it in a cookie.

    The active language is always set through ``django.utils.translation.activate``
    so both Python code and templates follow the same language.
    """

    COOKIE_NAME = "parsstore_lang"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        supported = {code for code, _ in LANGUAGES}
        requested = (request.GET.get("lang") or "").split("-")[0]
        if requested in supported:
            language = requested
        else:
            cookie = request.COOKIES.get(self.COOKIE_NAME, "")
            language = cookie if cookie in supported else DEFAULT_LANGUAGE

        translation.activate(language)
        request.language = language
        request.LANGUAGE_CODE = language
        response = self.get_response(request)
        response.setdefault("Content-Language", language)
        translation.deactivate()
        if requested in supported and request.COOKIES.get(self.COOKIE_NAME) != language:
            response.set_cookie(
                self.COOKIE_NAME,
                language,
                max_age=60 * 60 * 24 * 365,
                samesite="Lax",
                secure=not settings.DEBUG,
                httponly=False,
            )
        return response
