
from django.db.models import CASCADE
from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):
    name=models.CharField(max_length=100,verbose_name='分类名称')
    slug=models.SlugField(max_length=100,unique=True,verbose_name='URL别名')
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200,verbose_name='文章标题')
    slug = models.SlugField(max_length=200,unique=True,verbose_name='URL别名')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author= models.ForeignKey(User,on_delete=CASCADE)
    category = models.ForeignKey(Category, on_delete=CASCADE)
    status = models.CharField(max_length=100,choices=[('draft','草稿'),('published','已发布')],default='draft')
    def __str__(self):
        return self.title

class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE,related_name='comments')
    author=models.ForeignKey(User,on_delete=CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content







