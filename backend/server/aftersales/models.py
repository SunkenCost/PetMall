from django.db import models
from django.conf import settings
from shopper.models import OrderInfo


class AfterSales(models.Model):
    SALES_TYPE_CHOICES = (
        ('REFUND', '退款'),
        ('EXCHANGE', '换货'),
    )
    STATUS_CHOICES = (
        ('APPLYING', '申请中'),
        ('PROCESSING', '处理中'),
        ('COMPLETED', '已完成'),
        ('REJECTED', '已拒绝'),
    )
    id = models.BigAutoField('售后主键ID', primary_key=True)
    order = models.ForeignKey(OrderInfo, on_delete=models.RESTRICT, verbose_name='关联订单')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='aftersales_user', verbose_name='发起用户')
    sales_type = models.CharField('业务类型', max_length=20, choices=SALES_TYPE_CHOICES, default='REFUND')
    reason = models.CharField('退换理由', max_length=255, null=True, blank=True)
    refund_amount = models.DecimalField('退回金额', max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField('进度状态', max_length=20, choices=STATUS_CHOICES, default='APPLYING')
    handle_result = models.CharField('处理结果说明', max_length=255, null=True, blank=True)
    handler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='aftersales_handler', verbose_name='处理员工')
    create_time = models.DateTimeField('申请时间', auto_now_add=True)
    update_time = models.DateTimeField('处理时间', auto_now=True)

    class Meta:
        db_table = 'AfterSales'
        verbose_name = '售后服务记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"售后批单 - {self.id}"
