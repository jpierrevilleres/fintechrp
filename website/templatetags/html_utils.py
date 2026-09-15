import re
import html as _html

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_IMG_TAG_RE = re.compile(r'<img\b(?![^>]*\bloading=)([^>]*?)(/?)>', re.IGNORECASE)


@register.filter(is_safe=True)
def html_unescape(value):
    """Unescape HTML entities in the given text.

    This is safe for already-escaped template output because we use it after
    `striptags` and Django will still autoescape the result when rendering.
    Use: {{ text|striptags|html_unescape|truncatechars:120 }}
    """
    if value is None:
        return ''
    try:
        return _html.unescape(value)
    except Exception:
        return value


@register.filter
def lazy_images(value):
    """Mark up <img> tags in rich-text content (e.g. CKEditor article
    bodies) with loading="lazy" decoding="async" so offscreen images in
    long articles don't compete with the initial page load. Skips any
    <img> that already declares a loading attribute.

    Use in place of |safe: {{ article.body|lazy_images }}
    """
    if not value:
        return value
    try:
        return mark_safe(_IMG_TAG_RE.sub(
            lambda m: f'<img{m.group(1)} loading="lazy" decoding="async"{m.group(2)}>',
            str(value),
        ))
    except Exception:
        return mark_safe(value)


# Maps an article's category value to the filename prefix used by the
# placeholder images in static/img/. "trade" has no dedicated placeholder
# set yet (only finance/technology/real-estate exist) - falls back to
# finance's until real trade placeholder images are added.
_FALLBACK_IMAGE_SLUGS = {
    'finance': 'finance',
    'technology': 'technology',
    'real_estate': 'real-estate',
    'trade': 'finance',
}


@register.simple_tag
def fallback_image_path(category, index):
    """Static path for a category placeholder thumbnail, for articles
    with no featured_image. `index` cycles through 1-3 regardless of the
    caller's counter value (previously this used |divisibleby, which
    returns a bool, not a number, silently breaking the image path).
    """
    slug = _FALLBACK_IMAGE_SLUGS.get(category, 'finance')
    try:
        n = (int(index) - 1) % 3 + 1
    except (TypeError, ValueError):
        n = 1
    return f'img/{slug}-{n}.jpg'
