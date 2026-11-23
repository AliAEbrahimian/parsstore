from string import Formatter

from django import template

from core.i18n import t

register = template.Library()

_CATEGORY_KEYS = {
    "mechanical": "cat_mechanical",
    "electronic": "cat_electronic",
    "weft": "cat_weft",
    "drive": "cat_drive",
    "weaving": "cat_weaving",
    "tools": "cat_tools",
}


@register.filter
def cat_label(value):
    """Translate a product category name into the active language."""
    key = _CATEGORY_KEYS.get(value)
    return t(key) if key else value


@register.filter
def get_item(mapping, key):
    """Safely read a dictionary key from a template."""
    try:
        return mapping[key]
    except (KeyError, TypeError):
        return ""


@register.filter
def fmt(value, arg):
    """Insert one argument into ``{}`` or a named field such as ``{since}``."""
    try:
        fields = [
            name for _, name, _, _ in Formatter().parse(value) if name is not None
        ]
        if fields and all(name == "" for name in fields):
            return value.format(arg)
        return value.format(**{name: arg for name in fields if name})
    except (AttributeError, IndexError, KeyError, ValueError):
        return value


@register.simple_tag
def page_info(number, total):
    """Return the "Page n of total" text in the active language."""
    return t("page_of").format(n=number, total=total)


@register.simple_tag
def tr(key):
    """Filter-friendly equivalent of {{ T.key }}."""
    return t(key)
