from django.urls import reverse

from .content_i18n import get_content
from .i18n import LANGUAGES, current_language, flat
from .views import HOME_ANCHORS


def site_content(request):
    """Static content and bilingual link data for all templates."""
    home_url = reverse("core:home")
    lang = current_language()
    labels = flat(lang)
    content = get_content(lang)

    def home_anchor(fragment):
        return f"{home_url}?lang={lang}#{fragment}"

    nav_items = [
        ("nav_home", home_anchor(HOME_ANCHORS["home"])),
        ("nav_about", home_anchor(HOME_ANCHORS["about"])),
        ("nav_products", f"{reverse('core:product_list')}?lang={lang}"),
        ("nav_brands", home_anchor(HOME_ANCHORS["brands"])),
        ("nav_club", home_anchor(HOME_ANCHORS["club"])),
        ("nav_contact", home_anchor(HOME_ANCHORS["contact"])),
    ]

    # Keep current filters and search terms when switching language
    params = request.GET.copy()
    params.pop("lang", None)
    extra = params.urlencode()
    switch_urls = {
        code: f"{request.path}?lang={code}" + (f"&{extra}" if extra else "")
        for code, _ in LANGUAGES
    }

    return {
        "LANG": lang,
        "LANGUAGES": LANGUAGES,
        "T": labels,
        "SITE": content["SITE"],
        "NAV": [{"label": labels[key], "href": href} for key, href in nav_items],
        "BRANDS_FOOTER": content["BRANDS"],
        "SWITCH_URLS": switch_urls,
    }
