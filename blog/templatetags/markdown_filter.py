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


@register.filter(name='plain')
def plain_filter(value):
    """{{ post.content|plain|truncatechars:140 }} → 去掉 Markdown 语法的纯文本"""
    # 去掉图片
    text = re.sub(r'!\[.*?\]\(.*?\)', '[图片]', value)
    # 去掉链接，保留文字
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)
    # 去掉标题标记
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 去掉加粗/斜体
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    # 去掉行内代码
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text.strip()


@register.filter(name='first_image')
def first_image_filter(value):
    """{{ post.content|first_image }} → 正文里第一张图片的 URL，没有则返回空字符串"""
    m = re.search(r'!\[.*?\]\((.*?)\)', value)
    return m.group(1) if m else ''
