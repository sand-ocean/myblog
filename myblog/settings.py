"""
Django settings for myblog project.
"""

import os
from pathlib import Path
import dj_database_url

# ── 项目根目录 ──────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── 安全 ──────────────────
# DEBUG=True → 开发模式（本地）；False → 生产模式（Railway）
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']  # Railway 分配域名
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-swaeig^!j=utfov2s^k2qe(a*1pxr+3txn3q^p9b&3qso$6an#')

# Railway 跑在 HTTPS 代理后面，Django 需要知道
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://*.up.railway.app']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── 模块注册 ──────────────────
# Django 项目 = 多个 App 拼起来，每创建一个 App 就加到下面
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',           # 用户认证（User 模型、登录/登出）
    'django.contrib.contenttypes',
    'django.contrib.sessions',       # Session 管理（记住登录状态）
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',                          # 你的博客 App
]

# ── 中间件（请求处理管道）──────────────────
# 每个请求进 Django → 依次经过这些关卡 → 出 Django
# 你不用改，但要知道：CsrfViewMiddleware=CSRF保护，AuthenticationMiddleware=给request塞user
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myblog.urls'

# ── 模板配置 ──────────────────
# Django 找 HTML：① DIRS 里列出的目录 ② 每个 App 的 templates/ 目录
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myblog.wsgi.application'

# ── 数据库 ──────────────────
# 本地开发：SQLite；Railway 生产：自动检测 DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── 密码验证 ──────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── 国际化 ──────────────────
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'     # 生产环境：collectstatic 收集静态文件到这里

# ── 登录相关 ──────────────────
LOGIN_URL = '/login/'             # 未登录 → 跳转登录页
LOGIN_REDIRECT_URL = '/'          # 登录成功 → 跳转首页

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
