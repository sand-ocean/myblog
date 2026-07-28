"""
自动创建管理员账号。运行方式：
python manage.py setup_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = '创建管理员账号（用户名 admin，密码 admin123）'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write('管理员已存在，跳过')
            return
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.stdout.write('管理员创建成功：admin / admin123')
