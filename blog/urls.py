
from django.urls import path
from . import views, api_views  # 新增：导入 API 视图模块

urlpatterns = [
    # ── HTML 页面路由（浏览器访问）──────────────────
    path('', views.post_list, name='post_list'),
    # 固定路径必须在 <slug> 之前，否则 'new' 会被当成 slug
    path('post/new/', views.post_new, name='post_new'),
    path('register/', views.register, name='register'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/comment/', views.post_comments, name='post_comments'),
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('import/', views.import_post, name='import_post'),
    path('setup/', views.setup_init, name='setup_init'),

    # ── JSON API 路由（Apipost / Postman 用）──────
    # 注意：API 路由都以 api/ 开头，和上面的 HTML 路由不冲突
    path('api/posts/', api_views.api_post_list, name='api_post_list'),
    path('api/posts/<slug:slug>/', api_views.api_post_detail, name='api_post_detail'),
    path('api/posts/<slug:slug>/like/', api_views.api_like_post, name='api_like_post'),
    path('api/posts/<slug:slug>/comment/', api_views.api_post_comment, name='api_post_comment'),
    path('api/categories/', api_views.api_categories, name='api_categories'),
]
