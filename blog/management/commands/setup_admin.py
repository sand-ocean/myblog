"""
部署后初始化脚本。运行方式：
python manage.py setup_admin

做什么：
1. 创建管理员账号（如果不存在）
2. 创建默认分类（如果不存在）
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Category


class Command(BaseCommand):
    help = '初始化：创建管理员 + 默认分类（幂等，可重复运行）'

    def handle(self, *args, **options):
        # 1. 建管理员
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.SUCCESS('✓ 管理员已存在，跳过'))
        else:
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✓ 管理员创建成功：admin / admin123'))

        # 2. 建默认分类
        defaults = [
            ('python', 'Python'),
            ('django', 'Django'),
            ('life', '生活随笔'),
        ]
        for slug, name in defaults:
            obj, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ 分类「{name}」已创建'))
            else:
                self.stdout.write(f'  分类「{name}」已存在，跳过')

        self.stdout.write(self.style.SUCCESS('\n初始化完成'))
