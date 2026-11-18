from . import content


def site_content(request):
    """اطلاعات ثابت سایت (نام، تلفن، برندها …) برای همه‌ی قالب‌ها."""
    return {
        "SITE": content.SITE,
        "NAV": [
            {"label": "خانه", "href": "#home"},
            {"label": "درباره ما", "href": "#about"},
            {"label": "محصولات", "href": "#products"},
            {"label": "برندها", "href": "#brands"},
            {"label": "باشگاه مشتریان", "href": "#club"},
            {"label": "تماس", "href": "#contact"},
        ],
        "BRANDS_FOOTER": content.BRANDS,
    }
