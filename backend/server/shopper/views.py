from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Address, Cart, CartItem, OrderInfo, OrderItem, PetProfile
from .serializers import AddressSerializer, CartSerializer, CartItemSerializer, OrderInfoSerializer, PetProfileSerializer
from commodity.models import Product, Inventory
from accounts.models import User
from django.db import transaction
import time
import random

class UserResourceViewSet(viewsets.ModelViewSet):
    """
    通用基类：限制查询结果集为当前登录用户（毕设降级：如果没有登录，默认给 test1 用户）
    """
    def get_user(self):
        if self.request.user and self.request.user.is_authenticated:
            return self.request.user
        return User.objects.filter(username='test1').first()

    def get_queryset(self):
        user = self.get_user()
        if user:
            return self.queryset.filter(user=user)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(user=self.get_user())


class AddressViewSet(UserResourceViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def perform_create(self, serializer):
        """
        加固：如果新建时勾选了默认，先清空该用户的旧默认地址。
        """
        is_default = serializer.validated_data.get('is_default', False)
        user = self.get_user()
        if is_default:
            Address.objects.filter(user=user).update(is_default=False)
        serializer.save(user=user)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def set_default(self, request, pk=None):
        """
        核心逻辑：将该用户所有地址设为非默认，然后再将当前地址设为默认。
        """
        address = self.get_object()
        # 毕设降级逻辑：获取当前逻辑用户
        user = self.get_user()
        
        # 1. 全部置为 False
        Address.objects.filter(user=user).update(is_default=False)
        
        # 2. 当前置为 True
        address.is_default = True
        address.save()
        
        return Response({'detail': f'已成功将 {address.receiver_name} 设为默认地址'}, status=status.HTTP_200_OK)

class PetProfileViewSet(UserResourceViewSet):
    queryset = PetProfile.objects.all()
    serializer_class = PetProfileSerializer

class CartViewSet(viewsets.GenericViewSet):
    """
    购物车操作：一个用户拥有唯一的购物车
    """
    serializer_class = CartSerializer

    def get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        return User.objects.filter(username='test1').first()

    def get_or_create_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.get_user())
        return cart

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    """
    具体的加改删购物车商品项
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_cart(self):
        user = self.request.user if self.request.user.is_authenticated else User.objects.filter(username='test1').first()
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get_queryset(self):
        return self.queryset.filter(cart=self.get_cart())

    def perform_create(self, serializer):
        # 防重复加购逻辑，如果已经在购物车里，直接累加数量
        cart = self.get_cart()
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)
        
        exist_item = CartItem.objects.filter(cart=cart, product=product).first()
        if exist_item:
            exist_item.quantity += quantity
            exist_item.save()
        else:
            serializer.save(cart=cart)


class OrderViewSet(UserResourceViewSet):
    """
    核心：提交订单事务流转
    """
    queryset = OrderInfo.objects.all().order_by('-create_time')
    serializer_class = OrderInfoSerializer

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        user = self.get_user()
        address_id = request.data.get('address_id')
        cart_item_ids = request.data.get('cart_item_ids', [])
        
        if not address_id or not cart_item_ids:
            return Response({'detail': '缺少收货地址或购物车商品'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({'detail': '收货地址无效'}, status=status.HTTP_400_BAD_REQUEST)
        
        items = CartItem.objects.filter(id__in=cart_item_ids, cart__user=user)
        if not items.exists():
            return Response({'detail': '加购商品无效'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 扣减库存 & 计算总额
        total_amount = 0
        for item in items:
            inventory = Inventory.objects.select_for_update().get(product=item.product)
            if inventory.current_quantity < item.quantity:
                return Response({'detail': f'商品 {item.product.name} 库存不足'}, status=status.HTTP_400_BAD_REQUEST)
            inventory.current_quantity -= item.quantity
            inventory.save()
            total_amount += (item.product.price * item.quantity)
        
        # 2. 生成外部订单号
        order_no = f"O{time.strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}"

        # 3. 创建主订单快照
        order = OrderInfo.objects.create(
            order_no=order_no,
            user=user,
            receiver_name=address.receiver_name,
            receiver_phone=address.receiver_phone,
            receiver_address=f"{address.province or ''}{address.city or ''}{address.district or ''}{address.detail_address or ''}",
            total_amount=total_amount,
            status='PENDING'
        )

        # 4. 创建订单明细图并清理购物车
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity,
                subtotal=item.product.price * item.quantity
            )
            item.delete() # 结算后从购物车移除
            
        return Response({'detail': '订单创建成功', 'order_no': order.order_no}, status=status.HTTP_201_CREATED)
