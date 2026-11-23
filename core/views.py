import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags

from .content_i18n import get_content
from .forms import ClubSignupForm, InquiryForm
from .i18n import current_language, t
from .models import Product

logger = logging.getLogger(__name__)

HOME_ANCHORS = {
    "home": "home",
    "about": "about",
    "products": "products",
    "brands": "brands",
    "club": "club",
    "contact": "contact",
}


def _home_url(anchor="", query=""):
    params = f"lang={current_language()}"
    if query:
        params = f"{query}&{params}"
    url = f"{reverse('core:home')}?{params}"
    return f"{url}#{anchor}" if anchor else url


def home(request):
    prefill = _inquiry_prefill(request)
    inquiry_form = InquiryForm(initial={"message": prefill} if prefill else None)
    club_form = ClubSignupForm()

    if request.method == "POST":
        form_type = "club" if request.POST.get("form_type") == "club" else "inquiry"

        if form_type == "club":
            if _is_rate_limited(request, "club"):
                messages.error(request, t("msg_club_limited"))
                return redirect(_home_url("club"))

            club_form = ClubSignupForm(request.POST)
            if club_form.is_valid():
                customer = club_form.save()
                _notify_club_signup(customer)
                messages.success(request, t("msg_club_ok"))
                return redirect(_home_url("club"))
            messages.error(request, t("msg_club_errors"))
        else:
            if _is_rate_limited(request):
                messages.error(request, t("msg_inquiry_limited"))
                return redirect(_home_url("contact"))

            inquiry_form = InquiryForm(request.POST)
            if inquiry_form.is_valid():
                inquiry = inquiry_form.save()
                _notify_inquiry(inquiry)
                messages.success(request, t("msg_inquiry_ok"))
                return redirect(_home_url("contact"))
            messages.error(request, t("msg_inquiry_errors"))

    limit = getattr(settings, "PRODUCTS_HOME_LIMIT", 6)
    products = (
        Product.objects.filter(is_active=True)
        .prefetch_related("specs")
        .order_by("-is_featured", "sort_order", "name")[:limit]
    )
    content = get_content(current_language())

    context = {
        "brands": content["BRANDS"],
        "categories": content["CATEGORIES"],
        "features": content["FEATURES"],
        "stats": content["STATS"],
        "steps": content["STEPS"],
        "faq": content["FAQ"],
        "CLUB": content["CLUB"],
        "products": products,
        "products_total": Product.objects.filter(is_active=True).count(),
        "form": inquiry_form,
        "club_form": club_form,
    }
    return render(request, "core/home.html", context)


def product_list(request):
    """Full parts catalogue with search, filtering and pagination."""
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
        "home_contact_url": _home_url("contact"),
    }
    return render(request, "core/products.html", context)


def product_detail(request, pk):
    """Detail page for a part: specifications and how to request a quote."""
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
        {
            "product": product,
            "related": related,
            "home_contact_url": _home_url("contact", f"product={product.pk}"),
        },
    )


def page_not_found(request, exception=None):
    return render(request, "core/404.html", status=404)


def server_error(request):
    return render(request, "core/500.html", status=500)


# ---------------------------------------------------------------- helpers
def _products_page_size():
    """Catalogue page size clamped to a safe range (6 to 96)."""
    size = getattr(settings, "PRODUCTS_PAGE_SIZE", 24)
    return max(6, min(96, size))


def _inquiry_prefill(request):
    """Default inquiry text when the visitor came from a product page."""
    product_id = request.GET.get("product", "")
    # Reject non-ASCII, non-numeric or overly long numeric product IDs to avoid 500s
    if not product_id.isascii() or not product_id.isdigit() or len(product_id) > 12:
        return ""
    try:
        product = Product.objects.filter(pk=int(product_id), is_active=True).first()
    except (ValueError, OverflowError):
        return ""
    if not product:
        return ""
    return t("prefill").format(name=product.name)


def _client_ip(request):
    """Client IP; X-Forwarded-For is read only with trusted proxy settings."""
    fallback = request.META.get("REMOTE_ADDR") or "unknown"
    if not getattr(settings, "TRUST_PROXY_HEADERS", False):
        return fallback

    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not forwarded:
        return fallback
    parts = [part.strip() for part in forwarded.split(",") if part.strip()]
    if not parts:
        return fallback
    trusted = max(0, getattr(settings, "TRUSTED_PROXY_COUNT", 1))
    index = max(0, len(parts) - trusted - 1)
    return parts[index]


def _is_rate_limited(request, kind="inquiry"):
    """Atomic per-IP counters for inquiries and club signups."""
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
        # add + incr is atomic; concurrent requests cannot all see the same count

        cache.add(key, 0, window)
        try:
            count = cache.incr(key)
        except ValueError:  # key expired between the two operations
            cache.add(key, 0, window)
            count = cache.incr(key)
        return count > limit
    except Exception:  # cache failure must not block form submission
        logger.exception("Rate-limit cache failure")
        return False


def _send_mail_safely(subject, message, recipients, failure_message):
    """Send email without letting SMTP failures stop form submission."""
    recipients = [recipient for recipient in (recipients or []) if recipient]
    if not recipients:
        return
    try:
        send_mail(
            subject=strip_tags(str(subject)),
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception:  # email failure must not stop form submission
        logger.exception(failure_message)


def _split_recipients(value):
    """Split comma/semicolon-separated email addresses."""
    if not value:
        return []
    return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]


def _admin_recipient(setting_name, fallback_name="CONTACT_NOTIFY_EMAIL"):
    """Admin recipient: dedicated setting, shared fallback or staff users."""
    configured = getattr(settings, setting_name, "") or getattr(settings, fallback_name, "")
    recipients = _split_recipients(configured)
    if recipients:
        return recipients

    try:
        from django.contrib.auth import get_user_model

        return list(
            get_user_model()
            .objects.filter(is_active=True, is_staff=True)
            .exclude(email="")
            .values_list("email", flat=True)[:5]
        )
    except Exception:  # missing users table must not stop form submission
        logger.exception("Could not find an admin email recipient")
        return []


def _notify_inquiry(inquiry):
    """Send admin notification and customer confirmation for an inquiry."""
    safe_name = " ".join(inquiry.name.split())[:150]

    _send_mail_safely(
        subject=t("mail_new_inquiry").format(name=safe_name),
        message=(
            f"{t('f_name')}: {inquiry.name}\n"
            f"{t('f_company')}: {inquiry.company or '—'}\n"
            f"{t('f_phone')}: {inquiry.phone}\n"
            f"{t('f_email')}: {inquiry.email}\n"
            f"{t('f_machine')}: {inquiry.machine or '—'}\n\n"
            f"{t('f_message')}:\n{inquiry.message}"
        ),
        recipients=_admin_recipient("CONTACT_NOTIFY_EMAIL"),
        failure_message="Failed to send inquiry notification to admin",
    )

    _send_mail_safely(
        subject=t("mail_inquiry_subject"),
        message=(
            f"{inquiry.name},\n\n"
            + t("mail_inquiry_body")
            + f"\n\n{t('f_company')}: {inquiry.company or '—'}\n"
            + f"{t('f_phone')}: {inquiry.phone}\n"
            + f"{t('f_machine')}: {inquiry.machine or '—'}\n\n"
            + f"{t('f_message')}:\n{inquiry.message}\n\n"
            + t("mail_regards")
        ),
        recipients=[inquiry.email],
        failure_message="Failed to send inquiry confirmation to customer",
    )


def _notify_club_signup(customer):
    """Send admin notification and confirmation to a new club member."""
    safe_name = " ".join(customer.full_name.split())[:150]

    _send_mail_safely(
        subject=t("mail_new_club").format(name=safe_name),
        message=(
            f"{t('f_name')}: {customer.full_name}\n"
            f"{t('f_company')}: {customer.company or '—'}\n"
            f"{t('f_phone')}: {customer.phone}\n"
            f"{t('f_email')}: {customer.email}\n"
            f"Code: {customer.code}\n\n"
            + t("mail_activate_hint")
        ),
        recipients=_admin_recipient("CLUB_NOTIFY_EMAIL"),
        failure_message="Failed to send club notification to admin",
    )

    _send_mail_safely(
        subject=t("mail_club_subject"),
        message=(
            f"{customer.first_name},\n\n" + t("msg_club_ok") + "\n\n"
            f"{t('f_name')}: {customer.full_name}\n"
            f"{t('f_phone')}: {customer.phone}\n"
            f"{t('f_email')}: {customer.email}\n\n"
            f"Code: {customer.code}\n\n"
            + t("mail_discount_hint")
            + "\n\n"
            + t("mail_regards")
        ),
        recipients=[customer.email],
        failure_message="Failed to send club confirmation to customer",
    )
