from django.db import models
from django.contrib.auth.models import AbstractUser


class SysRole(models.Model):
    id = models.BigAutoField('角色主键ID', primary_key=True)
    role_name = models.CharField('角色显示名称', max_length=50)
    role_code = models.CharField('角色业务编码', max_length=50)
    description = models.CharField('角色职责描述', max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField('逻辑删除标识', default=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'SysRole'
        verbose_name = '角色管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    # 继承了 AbstractUser 的 username, password, first_name, last_name, email, is_staff, is_active, date_joined 等
    id = models.BigAutoField('用户主键ID', primary_key=True)
    real_name = models.CharField('真实姓名', max_length=50, null=True, blank=True)
    role = models.ForeignKey(SysRole, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='系统角色')
    phone = models.CharField('联系电话', max_length=11, null=True, blank=True)
    is_deleted = models.BooleanField('逻辑删除标识', default=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'User'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class SysPermission(models.Model):
    MENU_TYPES = (
        (1, '目录'),
        (2, '页面'),
        (3, '按钮'),
    )
    id = models.BigAutoField('权限主键ID', primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父级菜单')
    menu_name = models.CharField('菜单/按钮名称', max_length=50)
    route_path = models.CharField('路由地址', max_length=200, null=True, blank=True)
    perm_code = models.CharField('权限校验标识', max_length=100, null=True, blank=True)
    menu_type = models.SmallIntegerField('菜单类型', choices=MENU_TYPES, default=1)
    is_deleted = models.BooleanField('逻辑删除标识', default=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'SysPermission'
        verbose_name = '菜单权限管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.menu_name


class SysRolePermission(models.Model):
    id = models.BigAutoField('关联主键ID', primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.CASCADE, verbose_name='关联角色')
    permission = models.ForeignKey(SysPermission, on_delete=models.CASCADE, verbose_name='关联权限')

    class Meta:
        db_table = 'SysRolePermission'
        unique_together = ('role', 'permission')
        verbose_name = '角色权限关联'
        verbose_name_plural = verbose_name


class SysConfig(models.Model):
    id = models.BigAutoField('配置主键ID', primary_key=True)
    config_key = models.CharField('配置键名', max_length=100, unique=True)
    config_value = models.TextField('配置内容', null=True, blank=True)
    description = models.CharField('配置说明', max_length=255, null=True, blank=True)
    status = models.BooleanField('生效状态', default=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        db_table = 'SysConfig'
        verbose_name = '平台基础配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.config_key


class SystemErrorLog(models.Model):
    id = models.BigAutoField('日志主键ID', primary_key=True)
    request_url = models.CharField('接口地址', max_length=500, null=True, blank=True)
    error_stack = models.TextField('报错代码堆栈', null=True, blank=True)
    ip_address = models.CharField('触发IP', max_length=50, null=True, blank=True)
    process_status = models.BooleanField('修复状态', default=False)
    create_time = models.DateTimeField('报错时间', auto_now_add=True)

    class Meta:
        db_table = 'SystemErrorLog'
        verbose_name = '系统异常日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Log {self.id} - {self.create_time}"
