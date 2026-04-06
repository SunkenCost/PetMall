from django.contrib import admin
from .models import PetProfile, Address, Cart, CartItem, OrderInfo, OrderItem

@admin.register(PetProfile)
class PetProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pet_name', 'pet_type', 'gender', 'create_time')
    search_fields = ('pet_name', 'user__username')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'receiver_name', 'receiver_phone', 'is_default')
    search_fields = ('receiver_name', 'user__username')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'update_time')
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_no', 'user', 'total_amount', 'status', 'create_time')
    list_filter = ('status',)
    search_fields = ('order_no', 'user__username', 'receiver_name')
    inlines = [OrderItemInline]