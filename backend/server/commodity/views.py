from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    商品分类接口（仅支持查询列表和详情）
    """
    queryset = Category.objects.filter(status=True).order_by('sort_order')
    serializer_class = CategorySerializer
    pagination_class = None  # 分类一般不分页直接全拿

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    前端商品展示接口：
    支持搜索: /api/products/?search=猫粮
    支持排序: /api/products/?ordering=-sales (销量降序) 或 price (价格升序)
    支持分类过滤: /api/products/?category=1
    """
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sales', 'create_time']

    def get_queryset(self):
        # 默认只查询上架的商品 (status=True) 并且未被逻辑删除的
        queryset = Product.objects.filter(status=True, is_deleted=False).order_by('-create_time')
        
        # 自定义分类筛选
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset
