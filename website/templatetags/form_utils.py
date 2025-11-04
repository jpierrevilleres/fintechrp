from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def add_class(field, css_class):
    """Render field with the given CSS class appended to existing classes.

    Usage: {{ field|add_class:"form-control" }}
    If the widget already has a class, the new class is appended.
    """
    try:
        attrs = {}
        existing = field.field.widget.attrs.get('class', '')
        if existing:
            attrs['class'] = f"{existing} {css_class}"
        else:
            attrs['class'] = css_class
        return field.as_widget(attrs=attrs)
    except Exception:
        return field
