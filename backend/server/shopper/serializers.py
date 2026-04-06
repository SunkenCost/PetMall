from rest_framework import serializers
from .models import Address, Cart, CartItem, OrderInfo, OrderItem, PetProfile
from commodity.serializers import ProductSerializer

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']  # 防止用户故意篡改所属人

class PetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetProfile
        fields = '__all__'
        read_only_fields = ['user']

class CartItemSerializer(serializers.ModelSerializer):
    # 嵌套显示商品信息，方便前端直接展示购物车图片和价格
    product_detail = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'product_detail', 'create_time']
        read_only_fields = ['cart']  # 购物车ID应由后台自动绑定

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'update_time']
        read_only_fields = ['user']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderInfoSerializer(serializers.ModelSerializer):
    # 下单时嵌套创建或查询回显
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    
    class Meta:
        model = OrderInfo
        fields = '__all__'
        read_only_fields = ['user', 'order_no', 'status', 'total_amount'] # 这些由后端结算逻辑生成
