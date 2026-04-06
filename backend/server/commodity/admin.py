from django.contrib import admin
from .models import Category, Product, Inventory, InventoryLog

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'level', 'sort_order', 'status')
    list_filter = ('status', 'level')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'sales', 'colored_status')
    list_filter = ('status', 'category')
    search_fields = ('name',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'current_quantity', 'warning_threshold', 'update_time')
    search_fields = ('product__name',)

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'change_type', 'change_quantity', 'create_time')
    list_filter = ('change_type',)
