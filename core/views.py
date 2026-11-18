import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from . import content
from .forms import ClubSignupForm, InquiryForm
from .models import Product

logger = logging.getLogger(__name__)


def home(request):
    inquiry_form = InquiryForm()
    club_form = ClubSignupForm()

    if request.method == "POST":
        form_type = "club" if request.POST.get("form_type") == "club" else "inquiry"

        if form_type == "club":
            if _is_rate_limited(request, "club"):
                messages.error(
                    request,
                    "تعداد درخواست‌های عضویت از این دستگاه زیاد است. لطفاً کمی بعد دوباره تلاش کنید.",
                )
                return redirect(f"{reverse('core:home')}#club")

            club_form = ClubSignupForm(request.POST)
            if club_form.is_valid():
                customer = club_form.save()
                _notify_club(customer)
                messages.success(
                    request,
                    "درخواست عضویت شما ثبت شد. کارشناسان ما برای فعال‌سازی و اعلام کد عضویت با شما تماس می‌گیرند.",
                )
                return redirect(f"{reverse('core:home')}#club")
            messages.error(request, "لطفاً خطاهای فرم عضویت را برطرف کنید.")
        else:
            if _is_rate_limited(request):
                messages.error(
                    request,
                    "تعداد استعلام‌های ارسالی از این دستگاه زیاد است. لطفاً چند دقیقه بعد دوباره تلاش کنید.",
                )
                return redirect(f"{reverse('core:home')}#contact")

            inquiry_form = InquiryForm(request.POST)
            if inquiry_form.is_valid():
                inquiry = inquiry_form.save()
                _notify_owner(inquiry)
                messages.success(
                    request,
                    "استعلام شما ثبت شد. کارشناسان ما در کمتر از ۲۴ ساعت کاری با شما تماس می‌گیرند.",
                )
                return redirect(f"{reverse('core:home')}#contact")
            messages.error(request, "لطفاً خطاهای مشخص‌شده در فرم را برطرف کنید.")

    limit = getattr(settings, "PRODUCTS_HOME_LIMIT", 6)
    products = (
        Product.objects.filter(is_active=True)
        .prefetch_related("specs")
        .order_by("-is_featured", "sort_order", "name")[:limit]
    )

    context = {
        "site": content.SITE,
        "brands": content.BRANDS,
        "categories": content.CATEGORIES,
        "features": content.FEATURES,
        "stats": content.STATS,
        "steps": content.STEPS,
        "faq": content.FAQ,
        "CLUB": content.CLUB,
        "products": products,
        "form": inquiry_form,
        "club_form": club_form,
    }
    return render(request, "core/home.html", context)


def page_not_found(request, exception=None):
    return render(request, "core/404.html", status=404)


def server_error(request):
    return render(request, "core/500.html", status=500)


# ---------------------------------------------------------------- کمک‌تابع‌ها
def _client_ip(request):
    """IP مشتری؛ هدرهای پراکسی فقط با فعال‌سازی صریح DJANGO_TRUST_PROXY_HEADERS خوانده می‌شوند."""
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _is_rate_limited(request, kind="inquiry"):
    """محدودکردن تعداد درخواست فرم‌ها بر اساس IP.

    استعلام و عضویت باشگاه شمارندهٔ جدا دارند تا یکی دیگری را مسدود نکند.
    """
    if kind == "club":
        limit = getattr(settings, "CLUB_RATE_LIMIT", 4)
        window = getattr(settings, "CLUB_RATE_WINDOW", 3600)
    else:
        limit = getattr(settings, "INQUIRY_RATE_LIMIT", 6)
        window = getattr(settings, "INQUIRY_RATE_WINDOW", 600)
    if limit <= 0:
        return False

    key = f"{kind}-throttle:{_client_ip(request)}"
    try:
        count = cache.get(key, 0)
        if count >= limit:
            return True
        if count == 0:
            cache.add(key, 1, window)
        else:
            try:
                cache.incr(key)
            except ValueError:  # کلید بین دو عملیات منقضی شده است
                cache.set(key, count + 1, window)
    except Exception:  # خرابی کش نباید مانع ثبت درخواست شود
        logger.exception("خطا در محدودسازی نرخ درخواست‌ها")
        return False
    return False


def _notify_owner(inquiry):
    """اطلاع‌رسانی اختیاری با ایمیل؛ فقط اگر CONTACT_NOTIFY_EMAIL تنظیم شده باشد."""
    recipient = getattr(settings, "CONTACT_NOTIFY_EMAIL", "")
    if not recipient:
        return

    safe_name = " ".join(inquiry.name.split())[:150]
    try:
        send_mail(
            subject=f"استعلام جدید: {safe_name}",
            message=(
                f"نام: {inquiry.name}\n"
                f"شرکت: {inquiry.company or '—'}\n"
                f"تلفن: {inquiry.phone}\n"
                f"ماشین: {inquiry.machine or '—'}\n\n"
                f"توضیحات:\n{inquiry.message}"
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception:  # خطای ایمیل نباید ثبت استعلام را متوقف کند
        logger.exception("ارسال ایمیل اطلاع‌رسانی استعلام ناموفق بود")


def _notify_club(customer):
    """اطلاع‌رسانی اختیاری عضویت جدید به مدیر فروشگاه."""
    recipient = getattr(settings, "CONTACT_NOTIFY_EMAIL", "")
    if not recipient:
        return

    safe_name = " ".join(customer.full_name.split())[:150]
    try:
        send_mail(
            subject=f"درخواست عضویت باشگاه: {safe_name}",
            message=(
                f"نام: {customer.full_name}\n"
                f"شرکت: {customer.company or '—'}\n"
                f"تلفن: {customer.phone}\n"
                f"کد موقت: {customer.code}\n\n"
                "برای فعال‌سازی، وضعیت عضو را در پنل مدیریت روی «فعال» بگذارید."
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception:  # خطای ایمیل نباید ثبت عضویت را متوقف کند
        logger.exception("ارسال ایمیل اطلاع‌رسانی عضویت ناموفق بود")
