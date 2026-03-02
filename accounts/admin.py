from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


# Unregister the default User admin, then register our custom one (keeps edit/delete abilities)
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Admin: manage regular users (edit/delete)"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_editable = ('is_active',)
    actions = ['deactivate_users', 'activate_users']

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        n = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {n} user(s).')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, f'Activated {n} user(s).')
