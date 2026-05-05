from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Address, Cart, CartItem, OrderInfo, OrderItem, PetProfile
from .serializers import AddressSerializer, CartSerializer, CartItemSerializer, OrderInfoSerializer, PetProfileSerializer, PaymentRequestSerializer
from commodity.models import Product, Inventory
from accounts.models import User
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from .pays import get_pay_url, verify_alipay_callback
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


class PaymentViewSet(viewsets.GenericViewSet):
    """支付宝支付接口"""
    serializer_class = PaymentRequestSerializer
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """创建支付请求，返回支付宝支付链接
        
        请求体: { "order_no": "O20250101..." }
        返回: { "pay_url": "https://..." }
        """
        user = request.user if request.user.is_authenticated else User.objects.filter(username='test1').first()
        if not user:
            return Response({'detail': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
        
        order_no = request.data.get('order_no')
        if not order_no:
            return Response({'detail': '缺少订单号'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = OrderInfo.objects.get(order_no=order_no, user=user)
        except OrderInfo.DoesNotExist:
            return Response({'detail': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 只有待支付订单才能发起支付
        if order.status != 'PENDING':
            return Response({'detail': f'当前订单状态为 {order.status}，无法支付'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 构建商品标题（取第一个商品名）
        first_item = order.orderitem_set.first()
        subject = first_item.product_name if first_item else "PetMall订单"
        
        # 生成支付链接
        return_url = settings.ALIPAY_RETURN_URL
        pay_url = get_pay_url(
            out_trade_no=order.order_no,
            total_amount=order.total_amount,
            subject=subject,
            return_url=return_url,
        )
        
        return Response({'pay_url': pay_url, 'order_no': order.order_no, 'total_amount': str(order.total_amount)})
    
    @action(detail=False, methods=['get'], url_path='return')
    def payment_return(self, request):
        """支付宝同步回调页面
        
        用户支付完成后从支付宝跳转回来，携带订单信息
        注意：同步回调不做状态变更，状态由异步通知(notify)负责
        """
        out_trade_no = request.query_params.get('out_trade_no', '')
        trade_no = request.query_params.get('trade_no', '')
        total_amount = request.query_params.get('total_amount', '')
        
        # 返回前端完整 URL（使用 http://localhost:8010 前端地址）
        from django.http import HttpResponseRedirect
        frontend_url = f"http://localhost:8010/#/payment-result?out_trade_no={out_trade_no}&trade_no={trade_no}&total_amount={total_amount}"
        return HttpResponseRedirect(frontend_url)
    
    @action(detail=False, methods=['post'], url_path='notify')
    @method_decorator(csrf_exempt)
    def payment_notify(self, request):
        """支付宝异步通知回调"""
        callback_data = request.POST.dict()
        
        print(f"==================== 收到支付宝回调 ====================")
        print(f"Callback Data: {callback_data}")
        
        # 验证签名
        if not verify_alipay_callback(callback_data):
            print(f"!!! 支付宝异步通知 签名验证失败 !!!")
            return HttpResponse('fail')
        
        out_trade_no = callback_data.get('out_trade_no')
        trade_status = callback_data.get('trade_status')
        
        print(f"订单号: {out_trade_no}, 状态: {trade_status}")
        
        # 只有 TRADE_SUCCESS 和 TRADE_FINISHED 才更新订单
        if trade_status in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
            try:
                order = OrderInfo.objects.get(order_no=out_trade_no)
                callback_amount = callback_data.get('total_amount', '0')
                print(f"订单金额: {order.total_amount}, 回调金额: {callback_amount}")
                
                # 兼容可能是类似 146.0 和 146.00 的情况
                if float(order.total_amount) != float(callback_amount):
                    print(f"!!! 金额不匹配，订单失败 !!!")
                    return HttpResponse('fail')
                
                if order.status == 'PENDING':
                    order.status = 'PAID'
                    order.payment_method = 'alipay'
                    order.payment_time = timezone.now()
                    order.save()
                    print(f"订单 {out_trade_no} 状态已成功更新为 PAID")
                else:
                    print(f"订单 {out_trade_no} 状态已经是 {order.status}，无需重复更新")
            except OrderInfo.DoesNotExist:
                print(f"!!! 订单不存在: {out_trade_no} !!!")
                return HttpResponse('fail')
        
        # 返回 success 告诉支付宝已收到通知
        return HttpResponse('success')
    
    @action(detail=False, methods=['get'], url_path='query')
    def payment_query(self, request):
        """查询订单支付状态
        
        请求参数: ?order_no=O20250101...
        返回: { "status": "PAID", "order_no": "..." }
        """
        user = request.user if request.user.is_authenticated else User.objects.filter(username='test1').first()
        if not user:
            return Response({'detail': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
        
        order_no = request.query_params.get('order_no')
        if not order_no:
            return Response({'detail': '缺少订单号'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = OrderInfo.objects.get(order_no=order_no, user=user)
            return Response({
                'order_no': order.order_no,
                'status': order.status,
                'payment_method': order.payment_method,
                'total_amount': str(order.total_amount),
            })
        except OrderInfo.DoesNotExist:
            return Response({'detail': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
