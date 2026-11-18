from django.urls import reverse

from . import content


def site_content(request):
    """اطلاعات ثابت سایت (نام، تلفن، برندها …) برای همه‌ی قالب‌ها."""
    home_url = reverse("core:home")
    return {
        "SITE": content.SITE,
        "NAV": [
            {"label": "خانه", "href": f"{home_url}#home"},
            {"label": "درباره ما", "href": f"{home_url}#about"},
            {"label": "محصولات", "href": reverse("core:product_list")},
            {"label": "برندها", "href": f"{home_url}#brands"},
            {"label": "باشگاه مشتریان", "href": f"{home_url}#club"},
            {"label": "تماس", "href": f"{home_url}#contact"},
        ],
        "BRANDS_FOOTER": content.BRANDS,
    }
