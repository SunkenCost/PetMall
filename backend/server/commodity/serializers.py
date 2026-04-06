from rest_framework import serializers
from .models import Category, Product, Inventory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'level', 'sort_order']

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['current_quantity']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    inventory = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'main_image', 'description', 
            'price', 'old_price', 'sales', 'status',
            'category', 'category_name', 'inventory', 'create_time'
        ]

    def get_inventory(self, obj):
        # 尝试获取关联的库存数量，由于使用的是 OneToOne / 或者没有库存的情况做个保护
        inventory = Inventory.objects.filter(product=obj).first()
        if inventory:
            return inventory.current_quantity
        return 0

    def get_main_image(self, obj):
        if not obj.main_image:
            return None
        # 如果存的是远端完整 http(s) 地址，直接返回
        if str(obj.main_image).startswith('http'):
            return str(obj.main_image)
        # 否则按理说是本地 media 图片，返回完整路由
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.main_image.url)
        return obj.main_image.url
