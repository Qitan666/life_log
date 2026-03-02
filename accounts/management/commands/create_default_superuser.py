"""
创建默认管理员账号：用户名 admin，密码 123。
若已存在超级用户则跳过。执行：python manage.py create_default_superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = '创建默认管理员（admin / 123），仅当尚无超级用户时创建'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('已存在超级用户，跳过创建。'))
            return
        if User.objects.filter(username='admin').exists():
            # 存在 admin 但可能不是超级用户，改为设为超级用户并改密码
            user = User.objects.get(username='admin')
            user.set_password('123')
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS('已将用户 admin 设为超级用户并设置密码为 123。'))
            return
        User.objects.create_superuser('admin', '', '123')
        self.stdout.write(self.style.SUCCESS('默认管理员已创建：用户名 admin，密码 123。'))
