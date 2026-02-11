from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.filter(is_safe=True)
def markdown_to_html(text):
    """Convert Markdown text to safe HTML.

    Uses the `markdown` package and returns marked-safe HTML so templates
    can render rich content. If the package is not available this will
    raise ImportError (requirements.txt updated to include it).
    """
    if not text:
        return ''
    html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
    return mark_safe(html)
