from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SysRole, User, SysPermission, SysRolePermission, SysConfig, SystemErrorLog

@admin.register(SysRole)
class SysRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'role_name', 'role_code', 'is_deleted', 'create_time')
    search_fields = ('role_name', 'role_code')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'real_name', 'role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('real_name', 'role', 'phone', 'is_deleted')}),
    )

@admin.register(SysPermission)
class SysPermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'menu_name', 'menu_type', 'perm_code', 'route_path')
    list_filter = ('menu_type',)

@admin.register(SysRolePermission)
class SysRolePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission')

@admin.register(SysConfig)
class SysConfigAdmin(admin.ModelAdmin):
    list_display = ('config_key', 'config_value', 'status', 'update_time')
    search_fields = ('config_key',)

@admin.register(SystemErrorLog)
class SystemErrorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_url', 'ip_address', 'process_status', 'create_time')
    list_filter = ('process_status',)
