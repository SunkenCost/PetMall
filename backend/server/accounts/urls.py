from django.urls import path
from .views import (
    login, register,
    send_email_code, send_reset_code, reset_password,
    # 系统管理员接口
    admin_platform_stats,
    admin_user_list,
    admin_user_detail,
    admin_toggle_user_status,
    admin_grant_staff,
    admin_role_list,
    admin_error_log_list,
    admin_error_log_detail,
    admin_mark_log_fixed,
)

urlpatterns = [
    # ===== 认证相关 =====
    path('login/', login, name='api-login'),
    path('register/', register, name='api-register'),
    path('send-email-code/', send_email_code, name='api-send-email'),
    path('send-reset-code/', send_reset_code, name='api-send-reset'),
    path('reset-password/', reset_password, name='api-reset-pass'),

    # ===== 系统管理员接口（需 is_superuser Session 鉴权） =====
    path('admin/stats/', admin_platform_stats, name='admin-stats'),
    path('admin/users/', admin_user_list, name='admin-user-list'),
    path('admin/users/<int:user_id>/', admin_user_detail, name='admin-user-detail'),
    path('admin/users/<int:user_id>/toggle-status/', admin_toggle_user_status, name='admin-toggle-status'),
    path('admin/users/<int:user_id>/grant-staff/', admin_grant_staff, name='admin-grant-staff'),
    path('admin/roles/', admin_role_list, name='admin-role-list'),
    path('admin/error-logs/', admin_error_log_list, name='admin-error-log-list'),
    path('admin/error-logs/<int:log_id>/', admin_error_log_detail, name='admin-error-log-detail'),
    path('admin/error-logs/<int:log_id>/mark-fixed/', admin_mark_log_fixed, name='admin-mark-log-fixed'),
]
