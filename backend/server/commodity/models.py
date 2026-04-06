from django.db import models
from django.utils.html import format_html


class Category(models.Model):
    id = models.BigAutoField('分类主键ID', primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父级分类')
    name = models.CharField('分类名称', max_length=100)
    level = models.IntegerField('层级深度', default=1)
    sort_order = models.IntegerField('排序权重', default=0)
    status = models.BooleanField('启用状态', default=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'Category'
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.BigAutoField('商品主键ID', primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, verbose_name='所属分类')
    name = models.CharField('商品名称', max_length=200)
    main_image = models.FileField('商品主图', upload_to='imgs', null=True, blank=True)
    description = models.TextField('图文描述', null=True, blank=True)
    price = models.DecimalField('销售单价', max_digits=10, decimal_places=2, default=0.00)
    old_price = models.DecimalField('原价', max_digits=10, decimal_places=2, null=True, blank=True)
    sales = models.IntegerField('总销量', default=0)
    status = models.BooleanField('上架状态', default=True)  # True为上架, False为下架
    is_deleted = models.BooleanField('逻辑删除', default=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'Product'
        verbose_name = '商品信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    # 后台自定义显示方法
    def colored_status(self):
        if self.status:
            color_code = 'green'
            text = '已上架'
        else:
            color_code = 'red'
            text = '已下架'
        return format_html(
            '<span style="color: {};">{}</span>',
            color_code,
            text,
        )
    colored_status.short_description = '售卖状态'


class Inventory(models.Model):
    id = models.BigAutoField('库存主键ID', primary_key=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='关联商品')
    current_quantity = models.IntegerField('当前可卖数量', default=0)
    warning_threshold = models.IntegerField('预警阈值', default=10)
    version = models.IntegerField('乐观锁版本', default=0)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'Inventory'
        verbose_name = '商品库存记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.product.name} (库存:{self.current_quantity})"


class InventoryLog(models.Model):
    id = models.BigAutoField('流水主键ID', primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='监控商品')
    change_type = models.CharField('变动类型(IN/OUT)', max_length=20)
    change_quantity = models.IntegerField('变化数量')
    before_quantity = models.IntegerField('变动前库存')
    after_quantity = models.IntegerField('变动后库存')
    create_time = models.DateTimeField('发生时间', auto_now_add=True)

    class Meta:
        db_table = 'InventoryLog'
        verbose_name = '库存流水记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"流水 {self.id} | {self.change_type}"
