from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard,
    category_list,
    MerchantProductViewSet,
    MerchantInventoryViewSet,
    MerchantOrderViewSet,
    MerchantAfterSalesViewSet,
)

router = DefaultRouter()
router.register(r'products', MerchantProductViewSet, basename='merchant-product')
router.register(r'inventory', MerchantInventoryViewSet, basename='merchant-inventory')
router.register(r'orders', MerchantOrderViewSet, basename='merchant-order')
router.register(r'aftersales', MerchantAfterSalesViewSet, basename='merchant-aftersales')

urlpatterns = [
    path('dashboard/', dashboard, name='merchant-dashboard'),
    path('categories/', category_list, name='merchant-categories'),
    path('', include(router.urls)),
]
