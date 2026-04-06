from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from commodity.models import Product, Category, Inventory, InventoryLog
from shopper.models import OrderInfo, OrderItem
from aftersales.models import AfterSales
from accounts.models import User

from .serializers import (
    MerchantProductSerializer, MerchantInventorySerializer,
    MerchantOrderSerializer, MerchantAfterSalesSerializer,
    CategorySimpleSerializer,
)


class IsStaffMixin:
    """
    所有商家管理接口的权限校验 Mixin。
    毕设降级：如无登录会话，尝试从请求 header X-Admin-Username 获取管理员用户名以通过校验。
    """
    def get_admin_user(self):
        if self.request.user and self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                return self.request.user
        # 毕设降级：从请求头拿 admin username
        admin_username = self.request.META.get('HTTP_X_ADMIN_USERNAME', '')
        if admin_username:
            user = User.objects.filter(username=admin_username, is_staff=True).first()
            if user:
                return user
        return None

    def check_admin(self):
        user = self.get_admin_user()
        if not user:
            return Response({'detail': '需要商家管理员权限'}, status=status.HTTP_403_FORBIDDEN), None
        return None, user


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ======================== 数据看板 ========================

@api_view(['GET'])
def dashboard(request):
    """商家管理数据看板"""
    today = timezone.now().date()
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # 订单统计
    total_orders = OrderInfo.objects.count()
    today_orders = OrderInfo.objects.filter(create_time__date=today).count()
    pending_ship = OrderInfo.objects.filter(status='PAID').count()

    # 销售额
    total_revenue = OrderInfo.objects.filter(
        status__in=['PAID', 'SHIPPED', 'COMPLETED']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    monthly_revenue = OrderInfo.objects.filter(
        status__in=['PAID', 'SHIPPED', 'COMPLETED'],
        create_time__gte=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # 商品统计
    total_products = Product.objects.filter(is_deleted=False).count()
    on_shelf = Product.objects.filter(status=True, is_deleted=False).count()
    low_stock = Inventory.objects.filter(
        current_quantity__lte=10,
        product__status=True,
        product__is_deleted=False
    ).count()

    # 售后统计
    pending_aftersales = AfterSales.objects.filter(status__in=['APPLYING', 'PROCESSING']).count()

    # 近30天订单趋势（Python内存聚合，兼容SQLite）
    orders_30d = OrderInfo.objects.filter(create_time__gte=thirty_days_ago)
    trend_dict = {}
    
    # 填充基础天数以防止断桩
    for i in range(30):
        d = (today - timedelta(days=29 - i)).isoformat()
        trend_dict[d] = {'count': 0, 'revenue': 0}

    for order in orders_30d:
        if order.create_time:
            day_str = order.create_time.date().isoformat()
            if day_str in trend_dict:
                trend_dict[day_str]['count'] += 1
                trend_dict[day_str]['revenue'] += float(order.total_amount)

    trend_data = [{'date': k, 'count': v['count'], 'revenue': v['revenue']} for k, v in sorted(trend_dict.items())]

    return Response({
        'orders': {
            'total': total_orders,
            'today': today_orders,
            'pending_ship': pending_ship,
        },
        'revenue': {
            'total': float(total_revenue),
            'monthly': float(monthly_revenue),
        },
        'products': {
            'total': total_products,
            'on_shelf': on_shelf,
            'low_stock': low_stock,
        },
        'aftersales': {
            'pending': pending_aftersales,
        },
        'trend': trend_data,
    })


# ======================== 商品管理 ========================

class MerchantProductViewSet(IsStaffMixin, viewsets.ModelViewSet):
    serializer_class = MerchantProductSerializer
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['price', 'sales', 'create_time']

    def get_queryset(self):
        qs = Product.objects.filter(is_deleted=False).order_by('-create_time')
        # 支持状态筛选
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'on':
            qs = qs.filter(status=True)
        elif status_filter == 'off':
            qs = qs.filter(status=False)
        # 支持分类筛选
        category_id = self.request.query_params.get('category', None)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def list(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        response = super().create(request, *args, **kwargs)
        # 自动为新商品创建库存记录
        if response.status_code == status.HTTP_201_CREATED:
            product_id = response.data.get('id')
            if product_id:
                product = Product.objects.get(id=product_id)
                initial_qty = int(request.data.get('initial_qty', 0))
                Inventory.objects.get_or_create(
                    product=product,
                    defaults={'current_quantity': initial_qty, 'warning_threshold': 10}
                )
        return response

    def update(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        # 软删除
        instance = self.get_object()
        instance.is_deleted = True
        instance.status = False
        instance.save()
        return Response({'detail': '商品已下架并删除'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """切换商品上下架状态"""
        err, _ = self.check_admin()
        if err:
            return err
        product = self.get_object()
        product.status = not product.status
        product.save()
        label = '上架' if product.status else '下架'
        return Response({'detail': f'已{label}：{product.name}', 'status': product.status})

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


# ======================== 分类查询（给商品表单用） ========================

@api_view(['GET'])
def category_list(request):
    categories = Category.objects.filter(status=True).order_by('sort_order')
    serializer = CategorySimpleSerializer(categories, many=True)
    return Response(serializer.data)


# ======================== 库存管理 ========================

class MerchantInventoryViewSet(IsStaffMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = MerchantInventorySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Inventory.objects.select_related('product').filter(
            product__is_deleted=False
        ).order_by('current_quantity')
        # 支持低库存筛选
        low = self.request.query_params.get('low', None)
        if low == '1':
            qs = qs.filter(current_quantity__lte=10)
        return qs

    def list(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        """补货：调整库存数量"""
        err, admin = self.check_admin()
        if err:
            return err
        inventory = self.get_object()
        qty = int(request.data.get('quantity', 0))
        if qty <= 0:
            return Response({'detail': '补货数量必须大于0'}, status=status.HTTP_400_BAD_REQUEST)

        before = inventory.current_quantity
        inventory.current_quantity += qty
        inventory.save()

        # 记录库存流水
        InventoryLog.objects.create(
            product=inventory.product,
            change_type='IN',
            change_quantity=qty,
            before_quantity=before,
            after_quantity=inventory.current_quantity,
        )
        return Response({
            'detail': f'补货成功，当前库存 {inventory.current_quantity}',
            'current_quantity': inventory.current_quantity,
        })

    @action(detail=True, methods=['post'])
    def adjust(self, request, pk=None):
        """直接设置库存数量"""
        err, admin = self.check_admin()
        if err:
            return err
        inventory = self.get_object()
        qty = int(request.data.get('quantity', 0))
        if qty < 0:
            return Response({'detail': '库存数量不能为负'}, status=status.HTTP_400_BAD_REQUEST)

        before = inventory.current_quantity
        inventory.current_quantity = qty
        inventory.save()

        change = qty - before
        if change != 0:
            InventoryLog.objects.create(
                product=inventory.product,
                change_type='IN' if change > 0 else 'OUT',
                change_quantity=abs(change),
                before_quantity=before,
                after_quantity=qty,
            )
        return Response({
            'detail': f'库存已调整为 {qty}',
            'current_quantity': qty,
        })


# ======================== 订单管理 ========================

class MerchantOrderViewSet(IsStaffMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = MerchantOrderSerializer
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['order_no', 'receiver_name', 'receiver_phone', 'user__username']

    def get_queryset(self):
        qs = OrderInfo.objects.all().order_by('-create_time')
        order_status = self.request.query_params.get('status', None)
        if order_status:
            qs = qs.filter(status=order_status)
        return qs

    def list(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """发货：填入物流单号，将订单状态改为 SHIPPED"""
        err, admin = self.check_admin()
        if err:
            return err
        order = self.get_object()
        if order.status != 'PAID':
            return Response(
                {'detail': f'当前订单状态为「{order.get_status_display()}」，只有「已支付待发货」状态才能发货'},
                status=status.HTTP_400_BAD_REQUEST
            )
        logistics_no = request.data.get('logistics_no', '').strip()
        if not logistics_no:
            return Response({'detail': '请填写物流单号'}, status=status.HTTP_400_BAD_REQUEST)

        order.logistics_no = logistics_no
        order.status = 'SHIPPED'
        order.delivery_time = timezone.now()
        order.save()
        return Response({'detail': f'发货成功，物流单号：{logistics_no}'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """手动标记订单为完成"""
        err, admin = self.check_admin()
        if err:
            return err
        order = self.get_object()
        if order.status not in ['SHIPPED']:
            return Response({'detail': '只有已发货的订单才能标记完成'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'COMPLETED'
        order.save()
        return Response({'detail': '订单已标记为交易完成'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """关闭订单（针对长期未支付的订单）"""
        err, admin = self.check_admin()
        if err:
            return err
        order = self.get_object()
        if order.status != 'PENDING':
            return Response({'detail': '只有待支付的订单才能关闭'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'CLOSED'
        order.save()
        return Response({'detail': '订单已关闭'})


# ======================== 售后管理 ========================

class MerchantAfterSalesViewSet(IsStaffMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = MerchantAfterSalesSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = AfterSales.objects.all().order_by('-create_time')
        as_status = self.request.query_params.get('status', None)
        if as_status:
            qs = qs.filter(status=as_status)
        return qs

    def list(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        err, _ = self.check_admin()
        if err:
            return err
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        """处理售后申请：通过或拒绝"""
        err, admin = self.check_admin()
        if err:
            return err
        aftersales = self.get_object()
        if aftersales.status not in ['APPLYING', 'PROCESSING']:
            return Response({'detail': '该售后申请已处理完毕'}, status=status.HTTP_400_BAD_REQUEST)

        action_type = request.data.get('action')  # 'approve' or 'reject'
        handle_result = request.data.get('handle_result', '').strip()

        if action_type not in ['approve', 'reject']:
            return Response({'detail': 'action 只能是 approve（通过）或 reject（拒绝）'}, status=status.HTTP_400_BAD_REQUEST)

        aftersales.handle_result = handle_result
        aftersales.handler = admin
        if action_type == 'approve':
            aftersales.status = 'COMPLETED'
            msg = '售后申请已通过'
        else:
            aftersales.status = 'REJECTED'
            msg = '售后申请已拒绝'
        aftersales.save()
        return Response({'detail': msg})
