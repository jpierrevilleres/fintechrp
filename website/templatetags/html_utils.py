from django import template
import html as _html

register = template.Library()


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
