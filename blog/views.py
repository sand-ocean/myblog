from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Category
from .forms import PostForm, CommentForm
from django.db.models import Q
from django.core.paginator import Paginator


# ── 注册（不需登录）──────────────────
def register(request):
    """GET=显示注册表单  POST=创建用户并自动登录"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)              # 注册后自动登录
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# ── 首页（所有人可看）──────────────────
def post_list(request):
    """已登录看全部，未登录只看已发布"""
    if request.user.is_authenticated:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(status='published')
    posts = posts.order_by('-created_at')
    query = request.GET.get('q', '')  # 从 URL 取搜索词
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    paginator = Paginator(posts, 5)  # 每页5篇
    page_number = request.GET.get('page', 1)  # 当前第几页，默认1
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post_list.html', {'posts': posts,'page_obj':page_obj})



# ── 文章详情（所有人可看）──────────────────
def post_detail(request, slug):
    """文章详情 + 评论 + 草稿只有作者可见"""
    post = get_object_or_404(Post, slug=slug)
    if post.status == 'draft' and post.author != request.user:
        return redirect('post_list')
    comments = post.comments.all().order_by('-created_at')
    form = CommentForm()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


# ── 新建文章（需登录）──────────────────
@login_required
def post_new(request):
    """GET=空表单  POST=验证并保存，自动标记作者"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)    # 暂不写入
            post.author = request.user         # 补上作者
            post.save()                        # 现在写入
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})


# ── 编辑文章（需登录，只能改自己的）──────────────────
@login_required
def post_edit(request, slug):
    """只有作者本人能编辑"""
    post = get_object_or_404(Post, slug=slug)

    if post.author != request.user:            # 不是你的文章
        return redirect('post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)         # GET → 填充已有数据

    return render(request, 'blog/post_form.html', {'form': form})


# ── 删除文章（需登录，只能删自己的）──────────────────
@login_required
def post_delete(request, slug):
    """POST 才删除（防止误删），只有作者能删"""
    post = get_object_or_404(Post, slug=slug)

    if post.author != request.user:
        return redirect('post_list')

    if request.method == 'POST':
        post.delete()
        return redirect('post_list')

    return render(request, 'blog/post_detail.html', {'post': post})


# ── 按分类筛选 ──────────────────
def category_posts(request, slug):
    """展示某个分类下的所有文章"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).order_by('-created_at')
    return render(request, 'blog/category_posts.html', {
        'category': category,
        'posts': posts,
    })
@login_required
def post_comments(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post=post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', slug=post.slug)


# ── 点赞/取消点赞 ──────────────────
@login_required
def like_post(request, slug):
    """POST：如果没赞就点赞，赞过了就取消"""
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)   # 取消点赞
    else:
        post.likes.add(request.user)      # 点赞
    return redirect('post_detail', slug=slug)


# ── 一次性设置：初始化管理员+默认分类（部署后访问 /setup/）──────────────────
def setup_admin(request):
    """每次部署后访问此页面，自动建管理员和默认分类"""
    msg = []

    # 建管理员
    if User.objects.filter(username='admin').exists():
        msg.append('管理员已存在')
    else:
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        msg.append('管理员创建成功')

    # 建默认分类
    defaults = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('life', '生活随笔'),
    ]
    for slug, name in defaults:
        obj, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
        if created:
            msg.append(f'分类「{name}」已创建')
        else:
            msg.append(f'分类「{name}」已存在')

    msg.append('<br>账号：admin / admin123')
    msg.append('<br><a href="/admin/">去后台</a> | <a href="/">去首页</a>')
    return HttpResponse('<br>'.join(msg))


