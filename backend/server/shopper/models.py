from django.db import models
from django.conf import settings
from commodity.models import Product


class PetProfile(models.Model):
    id = models.BigAutoField('档案主键ID', primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='归属主子')
    pet_name = models.CharField('宠物昵称', max_length=50)
    pet_type = models.CharField('物种类别', max_length=20)
    breed = models.CharField('细分品种', max_length=50, null=True, blank=True)
    GENDER_CHOICES = (
        (0, '未知'),
        (1, '雄性'),
        (2, '雌性'),
    )
    gender = models.SmallIntegerField('性别', choices=GENDER_CHOICES, default=0)
    SIZE_CHOICES = (
        ('SMALL', '小型'),
        ('MEDIUM', '中型'),
        ('LARGE', '大型'),
    )
    size = models.CharField('体型', max_length=20, choices=SIZE_CHOICES, null=True, blank=True)
    birthday = models.DateField('破壳日', null=True, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'PetProfile'
        ordering = ['-create_time']
        verbose_name = '宠物档案管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} 的 {self.pet_name}"


class Address(models.Model):
    id = models.BigAutoField('地址主键ID', primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='所属用户')
    receiver_name = models.CharField('收件人', max_length=50)
    receiver_phone = models.CharField('联系电话', max_length=11)
    province = models.CharField('省份', max_length=50, null=True, blank=True)
    city = models.CharField('城市', max_length=50, null=True, blank=True)
    district = models.CharField('区县', max_length=50, null=True, blank=True)
    detail_address = models.CharField('详细地址', max_length=255, null=True, blank=True)
    is_default = models.BooleanField('设为默认', default=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'Address'
        ordering = ['-create_time']
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.receiver_name} - {self.detail_address}"


class Cart(models.Model):
    id = models.BigAutoField('购物车主键ID', primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='买家')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Cart'
        verbose_name = '购物车'
        verbose_name_plural = verbose_name


class CartItem(models.Model):
    id = models.BigAutoField('明细主键ID', primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='关联购物车')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='加购商品')
    quantity = models.IntegerField('选购数量', default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CartItem'
        verbose_name = '加购明细'
        verbose_name_plural = verbose_name


class OrderInfo(models.Model):
    STATUS_CHOICES = (
        ('PENDING', '待支付'),
        ('PAID', '已支付待发货'),
        ('SHIPPED', '已发货'),
        ('COMPLETED', '交易成功'),
        ('CLOSED', '已关闭'),
    )
    id = models.BigAutoField('订单主键ID', primary_key=True)
    order_no = models.CharField('业务发货单号', max_length=32, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, verbose_name='买家')
    # 地址快照
    receiver_name = models.CharField('收件人名称', max_length=50)
    receiver_phone = models.CharField('收件手机', max_length=11)
    receiver_address = models.CharField('落地位地址', max_length=255)
    
    total_amount = models.DecimalField('订单总计金额', max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField('结算管道', max_length=20, null=True, blank=True)
    status = models.CharField('交易状态', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    logistics_no = models.CharField('物流跟踪单号', max_length=100, null=True, blank=True)
    
    payment_time = models.DateTimeField('支付落库时间', null=True, blank=True)
    delivery_time = models.DateTimeField('出库打单时间', null=True, blank=True)
    create_time = models.DateTimeField('下单时间', auto_now_add=True)
    update_time = models.DateTimeField('记录刷新时间', auto_now=True)

    class Meta:
        db_table = 'OrderInfo'
        verbose_name = '交易订单主台'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"交易号: {self.order_no}"


class OrderItem(models.Model):
    id = models.BigAutoField('清单明细ID', primary_key=True)
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name='所属订单')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, verbose_name='发货商品')
    product_name = models.CharField('商品名称快照', max_length=200)
    product_price = models.DecimalField('成交单价快照', max_digits=10, decimal_places=2)
    quantity = models.IntegerField('拣货数', default=1)
    subtotal = models.DecimalField('行小计', max_digits=10, decimal_places=2)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'OrderItem'
        verbose_name = '交易订单明细'
        verbose_name_plural = verbose_name
