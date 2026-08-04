from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL别名')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='文章标题')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL别名')
    content = models.TextField(verbose_name='正文')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    status = models.CharField(
        max_length=10,
        choices=[('draft', '草稿'), ('published', '已发布')],
        default='draft',
        verbose_name='状态',
    )
    content_format = models.CharField(
        max_length=10,
        choices=[('markdown', 'Markdown'), ('html', 'HTML')],
        default='markdown',
        verbose_name='内容格式',
    )
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, verbose_name='点赞')

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

    def __str__(self):
        return self.content[:50]
