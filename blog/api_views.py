"""
============================================================================
blog/api_views.py —— JSON API 接口层
============================================================================
讲人话：这个文件专门给 Apipost / Postman 这类工具用的。
区别 —— 之前的 views.py 返回 HTML 网页（给人看的），
        这里的函数返回 JSON 字符串（给程序/工具读的）。

JSON 是什么？就是一种纯文本的数据格式，长这样：
{
    "id": 1,
    "title": "我的第一篇文章",
    "likes_count": 5,
    "liked": false
}
Apipost 读到这个 JSON，就能展示成一目了然的数据树。

学习要点：
  - JsonResponse: Django 内置，把一个 Python 字典自动转成 JSON
  - request.method: 判断请求是 GET(读) 还是 POST(写) 还是 DELETE(删)
  - @login_required: 强制登录才能访问
  - get_object_or_404: 找不到就返回 404，而不是崩溃
  - request.body: POST 请求的原始数据（JSON 格式的字符串）
  - json.loads(): 把 JSON 字符串 → Python 字典
============================================================================
"""

import json  # Python 内置，处理 JSON 数据的标准库

from django.http import JsonResponse
# ↑ JsonResponse 是 Django 内置的 HTTP 响应类。

from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
# ↑ authenticate: 验证用户名密码是否正确
#   login: 验证通过后创建 session，返回 Set-Cookie
# ↑ get_object_or_404：从数据库查一条数据，找不到自动返回 404。
#   等价于手动写：
#     try: post = Post.objects.get(slug=slug)
#     except Post.DoesNotExist: return HttpResponse(status=404)

from django.contrib.auth.decorators import login_required
# ↑ @login_required 装饰器：
#   放在函数定义的上面一行，自动拦截未登录的请求。
#   如果用户没登录 → 返回 302 重定向到登录页。
#   对于 API（非浏览器）请求 → 返回 403 Forbidden。

from django.views.decorators.csrf import csrf_exempt
# ↑ @csrf_exempt 装饰器：
#   Django 默认要求所有 POST 请求带 CSRF token（防跨站攻击）。
#   但 API 工具（Apipost/Postman）是服务端工具，没有 CSRF token。
#   加上这个装饰器 = 告诉 Django "这个接口不检查 CSRF，我信任它"。
#   ⚠️ 生产环境应该用 Token 认证，而不是简单关掉 CSRF！

from django.views.decorators.http import require_http_methods
# ↑ @require_http_methods：限制接口只能用指定的 HTTP 方法。
#   比如 @require_http_methods(["GET", "POST"])
#   如果有人用 DELETE 请求 → Django 自动返回 405 Method Not Allowed。
#   比在函数里写 if/elif 判断 method 更专业。

from .models import Post, Category, Comment
# ↑ 从当前目录的 models.py 导入数据模型。
#   . 表示"当前包"（即 blog/ 目录）。


# ============================================================================
# 接口 1：文章列表
# ============================================================================
# 请求方式: GET
# URL:      /api/posts/
# 参数:     ?page=1 & ?q=关键词（都可以不传）
#
# 返回示例:
# {
#     "posts": [ {...}, {...} ],    ← 文章数组，每篇是一个字典
#     "page": 1,                    ← 当前页码
#     "total_pages": 3,             ← 总页数
#     "total": 13,                  ← 总文章数
#     "has_next": true              ← 是否有下一页
# }
#
# Apipost 使用方法:
#   1. 打开 Apipost
#   2. 新建 GET 请求
#   3. URL 填: http://你的域名/api/posts/
#   4. 点发送 → 看到 JSON 格式的文章列表
#   5. 想搜素？URL 改成: http://你的域名/api/posts/?q=Python
# ============================================================================

@require_http_methods(["GET"])  # 只允许 GET 请求，POST/PUT 等一律 405
def api_post_list(request):
    """
    返回文章列表的 JSON 数据。

    和 views.py 里的 post_list 做的事情一样，只是输出格式不同：
    - views.post_list  → render(request, '模板.html', {...})  返回网页
    - api_post_list    → JsonResponse({...})                   返回 JSON
    """

    # ── 第 1 步：决定查哪些文章 ──────────────────────────
    # 已登录 → 看全部（包括草稿）
    # 未登录 → 只看已发布的
    if request.user.is_authenticated:
        posts = Post.objects.all()          # .all() 查全部
    else:
        posts = Post.objects.filter(status='published')  # .filter() 加条件

    # ── 第 2 步：搜索过滤 ──────────────────────────────
    # request.GET 是什么？
    #   URL 是 /api/posts/?q=Python
    #   那么 request.GET 就是 {'q': 'Python'}，一个字典
    #   .get('q', '') 意为取 q 的值，没有就返回空字符串 ''
    query = request.GET.get('q', '')
    if query:
        # Q 对象可以做"或"查询
        # title__icontains=query  → 标题包含关键词（不区分大小写）
        # content__icontains=query → 正文包含关键词
        # | 连接 → "标题或正文中任意一个包含就行"
        from django.db.models import Q
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    # ── 第 3 步：排序 ──────────────────────────────────
    # order_by('-created_at')
    #   减号 - 表示倒序（DESC）
    #   created_at 是创建时间
    #   连起来：按创建时间从新到旧排列
    posts = posts.order_by('-created_at')

    # ── 第 4 步：分页 ──────────────────────────────────
    # Paginator：Django 内置分页器
    #   Paginator(数据源, 每页条数)
    from django.core.paginator import Paginator
    paginator = Paginator(posts, 10)  # 每页 10 篇
    page_number = request.GET.get('page', 1)  # 从 URL 取页码，默认第 1 页
    page_obj = paginator.get_page(page_number)

    # ── 第 5 步：把文章对象变成字典列表 ─────────────────
    # 为什么要转换？因为 Post 是 Python 对象，JsonResponse 不认识。
    # 需要手动把每个 Post 对象 → Python 字典 → 最后变成 JSON。
    posts_data = []
    for post in page_obj:
        posts_data.append({
            # 左边是 JSON 里的键名  右边是从 Post 对象取的属性
            "id": post.id,
            "title": post.title,
            "slug": post.slug,          # URL 别名，用于拼接文章链接
            "author": post.author.username,  # 注意！author 是外键，要 .username
            "category": post.category.name,  # category 也是外键
            "status": post.status,      # draft 或 published
            "likes_count": post.likes.count(),  # ManyToMany 字段用 .count()
            "comments_count": post.comments.count(),
            "summary": post.content[:150],     # 截取前 150 字作摘要
            "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
            # ↑ datetime 对象 → 字符串，格式：2026-07-29 15:30
        })

    # ── 第 6 步：组装响应 ─────────────────────────────
    return JsonResponse({
        "posts": posts_data,
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total": paginator.count,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
    })
    # JsonResponse({...}) 做了什么？
    #   1. 把 Python 字典 → JSON 字符串
    #   2. 设置 Content-Type 响应头为 application/json
    #   3. 返回给客户端（Apipost/浏览器）


# ============================================================================
# 接口 2：文章详情
# ============================================================================
# 请求方式: GET
# URL:      /api/posts/<文章slug>/
# 示例:     /api/posts/hello-world/
#
# 返回示例:
# {
#     "id": 1,
#     "title": "Hello World",
#     "content": "这是正文内容...",
#     "author": "zzz1z",
#     "category": "Python",
#     "status": "published",
#     "likes_count": 5,
#     "liked": false,           ← 当前用户是否已点赞
#     "comments": [ {...} ],    ← 评论列表
#     "created_at": "2026-07-29 15:30",
#     "updated_at": "2026-07-29 16:00"
# }
# ============================================================================

@require_http_methods(["GET"])
def api_post_detail(request, slug):


    # get_object_or_404(Model, 条件)
    #   → 找到了：返回 Post 对象
    #   → 找不到：自动返回 404 JSON（不是崩溃！）
    post = get_object_or_404(Post, slug=slug)

    # ── 权限检查：草稿只有作者能看 ──────────────────────
    if post.status == 'draft' and post.author != request.user:
        return JsonResponse({"error": "文章不存在或无权访问"}, status=404)

    # ── 评论列表 ─────────────────────────────────────
    comments_data = []
    for comment in post.comments.all().order_by('-created_at'):
        comments_data.append({
            "id": comment.id,
            "author": comment.author.username,
            "content": comment.content,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    # ── 组装返回 ─────────────────────────────────────
    return JsonResponse({
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "author": post.author.username,
        "category": post.category.name,
        "status": post.status,
        "likes_count": post.likes.count(),
        # 判断当前用户是否已点赞
        # request.user.is_authenticated → 先检查是否登录
        # post.likes.filter(id=request.user.id).exists() → 再查点赞表
        # exists() 比 count() 更快——找到第一条就返回 True，不继续扫
        "liked": (
            request.user.is_authenticated
            and post.likes.filter(id=request.user.id).exists()
        ),
        "comments": comments_data,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
        "updated_at": post.updated_at.strftime("%Y-%m-%d %H:%M"),
    })


# ============================================================================
# 接口 3：点赞 / 取消点赞
# ============================================================================
# 请求方式: POST
# URL:      /api/posts/<文章slug>/like/
# 示例:     /api/posts/hello-world/like/
#
# 返回示例（点赞成功）:
# { "liked": true,  "likes_count": 6 }
#
# 返回示例（取消点赞）:
# { "liked": false, "likes_count": 5 }
#
# Apipost 使用方法:
#   1. 选择 POST 方法
#   2. URL: http://你的域名/api/posts/hello-world/like/
#   3. Headers 加: Content-Type: application/json
#   4. 点发送 → 看到点赞/取消结果
#   5. 再发一次 → 看到相反的结果（因为来回切换）
# ============================================================================

@require_http_methods(["POST"])   # 只允许 POST
@csrf_exempt                      # API 工具没有 CSRF token，先豁免
def api_like_post(request, slug):
    """
    点赞/取消点赞的 JSON 接口。

    逻辑和 views.py 里的 like_post 完全一样：
        已点赞 → 取消
        没点赞 → 点赞

    这叫"Toggle 模式"（开关模式）——同一个接口，点一下开，再点一下关。
    """

    # ── 第 0 步：检查是否登录 ─────────────────────────
    if not request.user.is_authenticated:
        return JsonResponse({"error": "请先登录"}, status=401)

    post = get_object_or_404(Post, slug=slug)

    # ── 检查是否已点赞 ───────────────────────────────
    if post.likes.filter(id=request.user.id).exists():
        # 已点赞 → 取消
        post.likes.remove(request.user)  # .remove() 删除关联记录
        liked = False
    else:
        # 未点赞 → 添加
        post.likes.add(request.user)     # .add() 创建关联记录
        liked = True

    # ── 返回结果 ─────────────────────────────────────
    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count(),
    })


# ============================================================================
# 接口 4：发表评论
# ============================================================================
# 请求方式: POST
# URL:      /api/posts/<文章slug>/comment/
# 请求体:   { "content": "这是一条评论" }
# 返回示例: { "id": 3, "author": "zzz1z", "content": "这是一条评论", "created_at": "..." }
#
# Apipost 使用方法:
#   1. 选择 POST 方法
#   2. URL: http://你的域名/api/posts/hello-world/comment/
#   3. Headers: Content-Type: application/json
#   4. Body → raw → JSON → 输入 {"content": "好文章！"}
#   5. 点发送
# ============================================================================

@require_http_methods(["POST"])
@csrf_exempt
def api_post_comment(request, slug):
    """
    发表评论的 JSON 接口。

    和 views.py 的 post_comments 不同：
    - 那边从 HTML 表单取数据：request.POST['content']
    - 这边从 JSON 请求体取数据：request.body → json.loads()
    """

    # ── 第 0 步：检查是否登录 ─────────────────────────
    if not request.user.is_authenticated:
        return JsonResponse({"error": "请先登录"}, status=401)
        # status=401 意为 "Unauthorized"——需要先验证身份

    post = get_object_or_404(Post, slug=slug)

    # ── 解析 JSON 请求体 ─────────────────────────────
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON 格式错误，请检查"}, status=400)

    content = data.get('content', '').strip()
    if not content:
        return JsonResponse({"error": "评论内容不能为空"}, status=400)

    # ── 保存评论 ─────────────────────────────────────
    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
    )
    # .create() 做了什么？
    #   1. 创建 Comment 对象
    #   2. 写入数据库（INSERT INTO）
    #   3. 返回新创建的 Comment 对象
    #   等价于 comment = Comment(...); comment.save()

    return JsonResponse({
        "id": comment.id,
        "author": comment.author.username,
        "content": comment.content,
        "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
    }, status=201)
    # status=201 意为 "Created"——数据已成功创建


# ============================================================================
# 接口 5：API 登录（免 CSRF，给 Apipost 用）
# ============================================================================
# 请求方式: POST
# URL:      /api/login/
# 请求体:   { "username": "admin", "password": "admin123" }
# 返回成功: { "ok": true, "username": "admin" }
# 返回失败: { "error": "用户名或密码错误", "ok": false }
#
# 重点：登录成功后 Django 会返回 Set-Cookie 响应头，
# Apipost 会自动保存 sessionid Cookie，后续请求自动带上。
# ============================================================================

@require_http_methods(["POST"])
@csrf_exempt
def api_login(request):
    """JSON 登录接口。成功后 session 自动写入 Cookie。"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON 格式错误"}, status=400)

    username = data.get('username', '')
    password = data.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"ok": False, "error": "用户名或密码错误"}, status=401)

    # login() 做了两件事：
    # 1. 在服务端创建 session 记录
    # 2. 在响应头里加 Set-Cookie: sessionid=xxx
    login(request, user)
    return JsonResponse({"ok": True, "username": user.username})

# ============================================================================
# 接口 6：分类列表
# ============================================================================
# 请求方式: GET
# URL:      /api/categories/
# 返回示例: [ {"id":1, "name":"Python", "slug":"python", "post_count":5}, ... ]
# ============================================================================

@require_http_methods(["GET"])
def api_categories(request):
    """返回所有分类的 JSON 列表。"""
    categories = []
    for cat in Category.objects.all():
        categories.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "post_count": cat.post_set.filter(status='published').count(),
            # ↑ cat.post_set 是 Django 自动生成的反向关联
            #   Category 和 Post 是一对多关系
            #   Category.post_set = 属于这个分类的所有 Post
        })
    return JsonResponse(categories, safe=False)
    # JsonResponse 的第一个参数必须是字典（dict），传列表会报错。
    # safe=False 告诉 Django："我知道传的是列表，放心，安全的。"
    # 如果不加 safe=False：
    #   TypeError: In order to allow non-dict objects to be serialized
    #   set the safe parameter to False.
