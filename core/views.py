import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from . import content
from .forms import ClubSignupForm, InquiryForm
from .models import Product

logger = logging.getLogger(__name__)


def home(request):
    prefill = _inquiry_prefill(request)
    inquiry_form = InquiryForm(initial={"message": prefill} if prefill else None)
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
                _notify_club_signup(customer)
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
                _notify_inquiry(inquiry)
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
        "products_total": Product.objects.filter(is_active=True).count(),
        "form": inquiry_form,
        "club_form": club_form,
    }
    return render(request, "core/home.html", context)


def product_list(request):
    """کاتالوگ کامل قطعات با جست‌وجو، فیلتر و صفحه‌بندی.

    صفحهٔ اصلی فقط چند محصول منتخب را نشان می‌دهد؛ این صفحه برای کاتالوگ
    ۸۰۰ تا ۱۲۰۰ قطعه ساخته شده و هر بار فقط یک صفحه از نتایج را می‌خواند.
    """
    q = (request.GET.get("q") or "").strip()[:80]
    category = request.GET.get("category", "")
    brand = (request.GET.get("brand") or "").strip()[:80]

    category_choices = Product.CATEGORY_CHOICES
    if category not in {value for value, _ in category_choices}:
        category = ""

    brand_options = list(
        Product.objects.filter(is_active=True)
        .exclude(brand="")
        .values_list("brand", flat=True)
        .distinct()
        .order_by("brand")
    )
    if brand not in brand_options:
        brand = ""

    products = Product.objects.filter(is_active=True).prefetch_related("specs")
    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(brand__icontains=q)
            | Q(machine_models__icontains=q)
            | Q(summary__icontains=q)
        )
    if category:
        products = products.filter(category=category)
    if brand:
        products = products.filter(brand=brand)
    products = products.order_by("-is_featured", "sort_order", "name")

    paginator = Paginator(products, _products_page_size())
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    page_items = [
        {"number": number, "is_ellipsis": number == Paginator.ELLIPSIS}
        for number in paginator.get_elided_page_range(
            page_obj.number, on_each_side=2, on_ends=1
        )
    ]

    context = {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "page_items": page_items,
        "querystring": querystring,
        "q": q,
        "category": category,
        "brand": brand,
        "category_choices": category_choices,
        "brand_options": brand_options,
        "has_filters": bool(q or category or brand),
        "result_count": paginator.count,
    }
    return render(request, "core/products.html", context)


def product_detail(request, pk):
    """صفحهٔ کامل یک قطعه؛ مشخصات فنی و راه استعلام قیمت."""
    product = get_object_or_404(
        Product.objects.filter(is_active=True).prefetch_related("specs"), pk=pk
    )
    related = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)
        .prefetch_related("specs")
        .order_by("-is_featured", "sort_order", "name")[:4]
    )
    return render(
        request,
        "core/product_detail.html",
        {"product": product, "related": related},
    )


def page_not_found(request, exception=None):
    return render(request, "core/404.html", status=404)


def server_error(request):
    return render(request, "core/500.html", status=500)


# ---------------------------------------------------------------- کمک‌تابع‌ها
def _products_page_size():
    """اندازهٔ صفحهٔ کاتالوگ با محدودهٔ امن (۶ تا ۹۶) برای جلوگیری از پاسخ سنگین."""
    size = getattr(settings, "PRODUCTS_PAGE_SIZE", 24)
    return max(6, min(96, size))


def _inquiry_prefill(request):
    """متن پیش‌فرض فرم استعلام وقتی کاربر از صفحهٔ محصول آمده است."""
    product_id = request.GET.get("product", "")
    if not product_id.isdigit():
        return ""
    product = (
        Product.objects.filter(pk=int(product_id), is_active=True)
        .only("name")
        .first()
    )
    if not product:
        return ""
    return f"استعلام قیمت برای: {product.name}"


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


def _send_mail_safely(subject, message, recipients, failure_message):
    """ارسال ایمیل بدون متوقف کردن ثبت فرم در صورت خرابی SMTP."""
    recipients = [recipient for recipient in (recipients or []) if recipient]
    if not recipients:
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception:  # خطای ایمیل نباید ثبت فرم را متوقف کند
        logger.exception(failure_message)


def _admin_recipient(setting_name, fallback_name="CONTACT_NOTIFY_EMAIL"):
    """گیرندهٔ ایمیل مدیر؛ تنظیم مخصوص، پیشفرض عمومی یا کاربران staff."""
    recipient = getattr(settings, setting_name, "") or getattr(
        settings, fallback_name, ""
    )
    if recipient:
        return [recipient]

    # اگر گیرندهای تنظیم نشده، ایمیل به کاربران فعال پنل مدیریت ارسال میشود.
    try:
        from django.contrib.auth import get_user_model

        return list(
            get_user_model()
            .objects.filter(is_active=True, is_staff=True)
            .exclude(email="")
            .values_list("email", flat=True)[:5]
        )
    except Exception:  # نبود جدول کاربران نباید مانع ثبت فرم شود
        logger.exception("یافتن گیرندهٔ ایمیل مدیر ناموفق بود")
        return []


def _notify_inquiry(inquiry):
    """ارسال دو ایمیل: اطلاع به مدیر و تأیید به مشتری."""
    safe_name = " ".join(inquiry.name.split())[:150]

    # ۱) ایمیل اطلاعرسانی به مدیر (اختیاری، برای سازگاری با نسخههای قبل)
    _send_mail_safely(
        subject=f"استعلام جدید: {safe_name}",
        message=(
            f"نام: {inquiry.name}\n"
            f"شرکت: {inquiry.company or '—'}\n"
            f"تلفن: {inquiry.phone}\n"
            f"ایمیل: {inquiry.email}\n"
            f"ماشین: {inquiry.machine or '—'}\n\n"
            f"توضیحات:\n{inquiry.message}"
        ),
        recipients=_admin_recipient("CONTACT_NOTIFY_EMAIL"),
        failure_message="ارسال ایمیل اطلاعرسانی استعلام به مدیر ناموفق بود",
    )

    # ۲) ایمیل تأیید به مشتری
    _send_mail_safely(
        subject="استعلام شما در پارس تکستایل ثبت شد",
        message=(
            f"{inquiry.name} عزیز،\n\n"
            "استعلام شما با موفقیت ثبت شد. کارشناسان ما در کمتر از ۲۴ ساعت کاری "
            "از طریق تلفن یا ایمیل با شما تماس میگیرند.\n\n"
            "خلاصهٔ درخواست:\n"
            f"شرکت: {inquiry.company or '—'}\n"
            f"تلفن: {inquiry.phone}\n"
            f"ماشین: {inquiry.machine or '—'}\n\n"
            f"توضیحات:\n{inquiry.message}\n\n"
            "با احترام،\nپارس تکستایل"
        ),
        recipients=[inquiry.email],
        failure_message="ارسال ایمیل تأیید استعلام به مشتری ناموفق بود",
    )


def _notify_club_signup(customer):
    """ارسال دو ایمیل: اطلاع به مدیر و تأیید به عضو جدید."""
    safe_name = " ".join(customer.full_name.split())[:150]

    # ۱) ایمیل اطلاعرسانی به مدیر
    _send_mail_safely(
        subject=f"درخواست عضویت باشگاه: {safe_name}",
        message=(
            f"نام: {customer.full_name}\n"
            f"شرکت: {customer.company or '—'}\n"
            f"تلفن: {customer.phone}\n"
            f"ایمیل: {customer.email}\n"
            f"کد موقت: {customer.code}\n\n"
            "برای فعالسازی، وضعیت عضو را در پنل مدیریت روی «فعال» بگذارید."
        ),
        recipients=_admin_recipient("CLUB_NOTIFY_EMAIL"),
        failure_message="ارسال ایمیل اطلاعرسانی عضویت به مدیر ناموفق بود",
    )

    # ۲) ایمیل تأیید به مشتری
    _send_mail_safely(
        subject="درخواست عضویت شما در باشگاه مشتریان ثبت شد",
        message=(
            f"{customer.first_name} عزیز،\n\n"
            "درخواست عضویت شما در باشگاه مشتریان پارس تکستایل ثبت شد. "
            "پس از تأیید کارشناسان ما، کد عضویت و میزان تخفیف شما اعلام میشود.\n\n"
            f"نام: {customer.full_name}\n"
            f"تلفن: {customer.phone}\n"
            f"ایمیل: {customer.email}\n\n"
            f"کد موقت: {customer.code}\n\n"
            "تخفیف باشگاه هنگام خرید حضوری یا تلفنی اعمال میشود.\n\n"
            "با احترام،\nپارس تکستایل"
        ),
        recipients=[customer.email],
        failure_message="ارسال ایمیل تأیید عضویت به مشتری ناموفق بود",
    )
