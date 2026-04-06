from rest_framework import serializers
from commodity.models import Product, Category, Inventory, InventoryLog
from shopper.models import OrderInfo, OrderItem
from aftersales.models import AfterSales
from accounts.models import User


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class MerchantProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    inventory_qty = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name',
            'price', 'old_price', 'sales',
            'status', 'is_deleted',
            'main_image', 'main_image_url',
            'description',
            'inventory_qty',
            'create_time', 'update_time',
        ]
        read_only_fields = ['id', 'sales', 'create_time', 'update_time']

    def get_inventory_qty(self, obj):
        try:
            return obj.inventory.current_quantity
        except Exception:
            return 0

    def get_main_image_url(self, obj):
        request = self.context.get('request')
        if obj.main_image and request:
            return request.build_absolute_uri(obj.main_image.url)
        return None


class MerchantInventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_status = serializers.BooleanField(source='product.status', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'product_id', 'product_name', 'product_price', 'product_status',
            'current_quantity', 'warning_threshold',
            'update_time',
        ]
        read_only_fields = ['id', 'product_id', 'product_name', 'product_price', 'product_status', 'update_time']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_price', 'quantity', 'subtotal']


class MerchantOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='orderitem_set', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderInfo
        fields = [
            'id', 'order_no', 'username', 'user_id',
            'receiver_name', 'receiver_phone', 'receiver_address',
            'total_amount', 'payment_method', 'status', 'status_display',
            'logistics_no',
            'payment_time', 'delivery_time',
            'create_time', 'update_time',
            'items',
        ]


class MerchantAfterSalesSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    sales_type_display = serializers.CharField(source='get_sales_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    handler_name = serializers.SerializerMethodField()

    class Meta:
        model = AfterSales
        fields = [
            'id', 'order_no', 'order_id', 'username', 'user_id',
            'sales_type', 'sales_type_display',
            'reason', 'refund_amount',
            'status', 'status_display',
            'handle_result', 'handler_id', 'handler_name',
            'create_time', 'update_time',
        ]

    def get_handler_name(self, obj):
        if obj.handler:
            return obj.handler.username
        return None
