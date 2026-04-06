from django.contrib import admin
from .models import AfterSales

@admin.register(AfterSales)
class AfterSalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'sales_type', 'status', 'refund_amount', 'create_time')
    list_filter = ('sales_type', 'status')
    search_fields = ('order__order_no', 'user__username')
