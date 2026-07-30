"""自定义模板过滤器：把 Markdown 文本转成 HTML"""
import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(value):
    """{{ post.content|markdown }} → 渲染后的 HTML"""
    html = md.markdown(
        value,
        extensions=['fenced_code', 'tables', 'nl2br'],
    )
    return mark_safe(html)
