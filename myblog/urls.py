"""
项目级 URL 路由表——把 URL 分发给对应的 App 处理。
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 登录/退出（Django 内置，一行代码搞定）
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/login/'
    ), name='logout'),

    # 后台管理
    path('admin/', admin.site.urls),

    # blog App 的所有路由 → 交给 blog/urls.py 处理
    path('', include('blog.urls')),
]
