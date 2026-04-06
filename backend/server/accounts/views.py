import random
from django.contrib.auth import authenticate, login as django_login
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from .models import User, SysRole, SystemErrorLog


# ==================== 权限校验工具 ====================

def _require_superuser(request):
    """
    严格的超级管理员权限校验。
    必须通过 Session 登录，且 is_superuser=True。
    返回 (error_response | None, user | None)
    """
    if not request.user or not request.user.is_authenticated:
        return Response({'detail': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED), None
    if not request.user.is_superuser:
        return Response({'detail': '需要系统管理员权限'}, status=status.HTTP_403_FORBIDDEN), None
    return None, request.user


# ==================== 认证相关 ====================

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = User.objects.filter(username=username).first()
    if user and user.check_password(password):
        if not getattr(user, 'is_active', True):
            return Response({'detail': '无权访问或账户被冻结'}, status=status.HTTP_403_FORBIDDEN)

        # ★ 写入 Django Session，使超管接口可通过 request.user 严格鉴权
        django_login(request, user)

        return Response({
            'id': user.id,
            'username': user.username,
            'realName': user.real_name,
            'email': getattr(user, 'email', ''),
            'phone': getattr(user, 'phone', ''),
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
        })
    else:
        return Response({'detail': '账号或密码错误'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def send_email_code(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': '请输入邮箱地址'}, status=status.HTTP_400_BAD_REQUEST)

    if cache.get(f'email_lock_{email}'):
        return Response({'detail': '请勿频繁点击获取验证码'}, status=status.HTTP_400_BAD_REQUEST)

    code = f"{random.randint(100000, 999999)}"
    try:
        send_mail(
            subject='【宠爱之家 PetMall】您的注册验证码',
            message=f'欢迎注册宠爱之家商城。\n您的专属邮箱验证码是：{code}，请在 {settings.EMAIL_CODE_EXPIRE_SECONDS//60} 分钟内完成注册。\n如非本人获取，请忽略本邮件。',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        cache.set(f'email_code_{email}', code, timeout=settings.EMAIL_CODE_EXPIRE_SECONDS)
        cache.set(f'email_lock_{email}', '1', timeout=60)
        return Response({'detail': '验证码发送成功'})
    except Exception as e:
        print("发送邮件报错:", e)
        return Response({'detail': '邮件服务开小差了，请检查邮箱配置'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def send_reset_code(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': '请输入邮箱地址'}, status=status.HTTP_400_BAD_REQUEST)

    if not User.objects.filter(email=email).exists():
        return Response({'detail': '该邮箱尚未注册'}, status=status.HTTP_400_BAD_REQUEST)

    if cache.get(f'email_lock_{email}'):
        return Response({'detail': '请勿频繁点击获取验证码'}, status=status.HTTP_400_BAD_REQUEST)

    code = f"{random.randint(100000, 999999)}"
    try:
        send_mail(
            subject='【宠爱之家 PetMall】重置密码验证码',
            message=f'您正在尝试重置密码。\n您的验证码是：{code}，请在 {settings.EMAIL_CODE_EXPIRE_SECONDS//60} 分钟内完成操作。\n若非本人操作，请及时检查账户安全。',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        cache.set(f'reset_code_{email}', code, timeout=settings.EMAIL_CODE_EXPIRE_SECONDS)
        cache.set(f'email_lock_{email}', '1', timeout=60)
        return Response({'detail': '重置验证码已发送'})
    except Exception as e:
        print("发送重置邮件报错:", e)
        return Response({'detail': '邮件发送失败，请检查配置'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')

    if not email or not code or not new_password:
        return Response({'detail': '邮箱、验证码、新密码均为必填项'}, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 6:
        return Response({'detail': '密码长度不能少于6位'}, status=status.HTTP_400_BAD_REQUEST)

    saved_code = cache.get(f'reset_code_{email}')
    if not saved_code or str(saved_code) != str(code):
        return Response({'detail': '验证码不正确或已过期'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    user.set_password(new_password)
    user.save()

    cache.delete(f'reset_code_{email}')
    return Response({'detail': '密码重置成功，请重新登录'})


@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    real_name = request.data.get('real_name', '')
    email = request.data.get('email', '')
    code = request.data.get('code')

    if not username or not password or not email or not code:
        return Response({'detail': '信息填写不完整，用户名/密码/邮箱/验证码皆为必填'}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 6:
        return Response({'detail': '密码长度不能少于6位'}, status=status.HTTP_400_BAD_REQUEST)

    saved_code = cache.get(f'email_code_{email}')
    if not saved_code or str(saved_code) != str(code):
        return Response({'detail': '验证码错误或已过期，请重新获取'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'detail': '该账号已被注册'}, status=status.HTTP_400_BAD_REQUEST)

    user_role, _ = SysRole.objects.get_or_create(role_code='USER', defaults={'role_name': '普通买家'})
    user = User.objects.create_user(
        username=username,
        password=password,
        real_name=real_name,
        email=email,
        role=user_role
    )
    cache.delete(f'email_code_{email}')
    return Response({'detail': '注册成功，快去登录吧~'}, status=status.HTTP_201_CREATED)


# ==================== 系统管理员 API ====================

class AdminPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def admin_platform_stats(request):
    """平台总览统计数据"""
    err, _ = _require_superuser(request)
    if err:
        return err

    today = timezone.now().date()
    thirty_days_ago = timezone.now() - timedelta(days=30)

    total_users = User.objects.filter(is_deleted=False).count()
    today_registered = User.objects.filter(
        date_joined__date=today, is_deleted=False
    ).count()
    monthly_registered = User.objects.filter(
        date_joined__gte=thirty_days_ago, is_deleted=False
    ).count()
    active_users = User.objects.filter(is_active=True, is_deleted=False).count()
    frozen_users = User.objects.filter(is_active=False, is_deleted=False).count()
    staff_count = User.objects.filter(is_staff=True, is_deleted=False).count()
    superuser_count = User.objects.filter(is_superuser=True, is_deleted=False).count()

    total_logs = SystemErrorLog.objects.count()
    pending_logs = SystemErrorLog.objects.filter(process_status=False).count()

    return Response({
        'users': {
            'total': total_users,
            'today_registered': today_registered,
            'monthly_registered': monthly_registered,
            'active': active_users,
            'frozen': frozen_users,
            'staff': staff_count,
            'superuser': superuser_count,
        },
        'system_logs': {
            'total': total_logs,
            'pending': pending_logs,
        },
    })


@api_view(['GET'])
def admin_user_list(request):
    """用户列表（分页 + 搜索 + 角色/状态筛选）"""
    err, _ = _require_superuser(request)
    if err:
        return err

    qs = User.objects.filter(is_deleted=False).select_related('role').order_by('-date_joined')

    # 关键词搜索
    keyword = request.query_params.get('keyword', '').strip()
    if keyword:
        qs = qs.filter(
            Q(username__icontains=keyword) |
            Q(real_name__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(phone__icontains=keyword)
        )

    # 状态筛选
    user_status = request.query_params.get('status', '')
    if user_status == 'active':
        qs = qs.filter(is_active=True)
    elif user_status == 'frozen':
        qs = qs.filter(is_active=False)

    # 权限筛选
    role_filter = request.query_params.get('role', '')
    if role_filter == 'superuser':
        qs = qs.filter(is_superuser=True)
    elif role_filter == 'staff':
        qs = qs.filter(is_staff=True, is_superuser=False)
    elif role_filter == 'user':
        qs = qs.filter(is_staff=False, is_superuser=False)

    paginator = AdminPagination()
    page = paginator.paginate_queryset(qs, request)

    data = []
    for u in page:
        data.append({
            'id': u.id,
            'username': u.username,
            'real_name': u.real_name or '',
            'email': u.email or '',
            'phone': u.phone or '',
            'is_active': u.is_active,
            'is_staff': u.is_staff,
            'is_superuser': u.is_superuser,
            'role_name': u.role.role_name if u.role else '—',
            'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M'),
            'last_login': u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else '从未登录',
        })

    return paginator.get_paginated_response(data)


@api_view(['GET'])
def admin_user_detail(request, user_id):
    """用户详情"""
    err, _ = _require_superuser(request)
    if err:
        return err

    user = User.objects.filter(id=user_id, is_deleted=False).select_related('role').first()
    if not user:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'id': user.id,
        'username': user.username,
        'real_name': user.real_name or '',
        'email': user.email or '',
        'phone': user.phone or '',
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'role_name': user.role.role_name if user.role else '—',
        'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M'),
        'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '从未登录',
    })


@api_view(['POST'])
def admin_toggle_user_status(request, user_id):
    """冻结 / 解冻用户账户"""
    err, admin = _require_superuser(request)
    if err:
        return err

    user = User.objects.filter(id=user_id, is_deleted=False).first()
    if not user:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_superuser:
        return Response({'detail': '不能冻结超级管理员账户'}, status=status.HTTP_400_BAD_REQUEST)

    if user.id == admin.id:
        return Response({'detail': '不能冻结自己的账户'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = not user.is_active
    user.save()

    label = '正常' if user.is_active else '已冻结'
    action = '解冻' if user.is_active else '冻结'
    return Response({
        'detail': f'已{action}用户「{user.username}」',
        'is_active': user.is_active,
        'status_label': label,
    })


@api_view(['POST'])
def admin_grant_staff(request, user_id):
    """授予 / 撤销商家管理员权限 (is_staff)"""
    err, admin = _require_superuser(request)
    if err:
        return err

    user = User.objects.filter(id=user_id, is_deleted=False).first()
    if not user:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_superuser:
        return Response({'detail': '超管账户权限无需调整'}, status=status.HTTP_400_BAD_REQUEST)

    if user.id == admin.id:
        return Response({'detail': '不能修改自己的权限'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_staff = not user.is_staff

    # 同步更新角色字段（便于业务展示）
    if user.is_staff:
        staff_role, _ = SysRole.objects.get_or_create(
            role_code='STAFF', defaults={'role_name': '商家管理员'}
        )
        user.role = staff_role
    else:
        user_role, _ = SysRole.objects.get_or_create(
            role_code='USER', defaults={'role_name': '普通买家'}
        )
        user.role = user_role

    user.save()

    label = '商家管理员' if user.is_staff else '普通买家'
    action = '授予' if user.is_staff else '撤销'
    return Response({
        'detail': f'已{action}「{user.username}」的商家权限',
        'is_staff': user.is_staff,
        'role_label': label,
    })


@api_view(['GET'])
def admin_role_list(request):
    """角色列表"""
    err, _ = _require_superuser(request)
    if err:
        return err

    roles = SysRole.objects.filter(is_deleted=False).order_by('id')
    data = [
        {
            'id': r.id,
            'role_name': r.role_name,
            'role_code': r.role_code,
            'description': r.description or '',
        }
        for r in roles
    ]
    return Response(data)


@api_view(['GET'])
def admin_error_log_list(request):
    """系统错误日志列表（分页）"""
    err, _ = _require_superuser(request)
    if err:
        return err

    qs = SystemErrorLog.objects.all().order_by('-create_time')

    # 状态筛选
    log_status = request.query_params.get('status', '')
    if log_status == 'pending':
        qs = qs.filter(process_status=False)
    elif log_status == 'fixed':
        qs = qs.filter(process_status=True)

    paginator = AdminPagination()
    page = paginator.paginate_queryset(qs, request)

    data = [
        {
            'id': log.id,
            'request_url': log.request_url or '',
            'error_stack': (log.error_stack or '')[:500],  # 截断，前端展开时再请求详情
            'ip_address': log.ip_address or '',
            'process_status': log.process_status,
            'create_time': log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for log in page
    ]

    return paginator.get_paginated_response(data)


@api_view(['GET'])
def admin_error_log_detail(request, log_id):
    """错误日志详情（完整堆栈）"""
    err, _ = _require_superuser(request)
    if err:
        return err

    log = SystemErrorLog.objects.filter(id=log_id).first()
    if not log:
        return Response({'detail': '日志记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'id': log.id,
        'request_url': log.request_url or '',
        'error_stack': log.error_stack or '',
        'ip_address': log.ip_address or '',
        'process_status': log.process_status,
        'create_time': log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
    })


@api_view(['POST'])
def admin_mark_log_fixed(request, log_id):
    """将错误日志标记为已修复"""
    err, _ = _require_superuser(request)
    if err:
        return err

    log = SystemErrorLog.objects.filter(id=log_id).first()
    if not log:
        return Response({'detail': '日志记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    if log.process_status:
        return Response({'detail': '该日志已标记为已修复'}, status=status.HTTP_400_BAD_REQUEST)

    log.process_status = True
    log.save()
    return Response({'detail': '已标记为修复完成', 'process_status': True})
