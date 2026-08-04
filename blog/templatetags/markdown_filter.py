"""自定义模板过滤器：Markdown 渲染 + 纯文本提取"""
import re
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


def _is_html(value):
    """内容是否像 HTML（有标签）"""
    return bool(re.search(r'<(p|h[1-6]|div|img|ul|ol|li|blockquote|pre|code|table|a|br|hr)\b', value))


@register.filter(name='plain')
def plain_filter(value):
    """{{ post.content|plain|truncatechars:140 }} → 纯文本摘要，兼容 Markdown 和 HTML"""
    if _is_html(value):
        # HTML：去掉所有标签，留下文字
        text = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*/?>', r'[\1]', value)  # img alt → 占位
        text = re.sub(r'<img[^>]*/?>', '[图片]', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    # Markdown
    text = re.sub(r'!\[.*?\]\(.*?\)', '[图片]', value)
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text.strip()


@register.filter(name='first_image')
def first_image_filter(value):
    """{{ post.content|first_image }} → 正文里第一张图片 URL，兼容 Markdown 和 HTML"""
    # HTML: <img src="...">
    m = re.search(r'<img[^>]+src="([^"]+)"', value)
    if m:
        return m.group(1)
    # Markdown: ![alt](url)
    m = re.search(r'!\[.*?\]\((.*?)\)', value)
    return m.group(1) if m else ''
