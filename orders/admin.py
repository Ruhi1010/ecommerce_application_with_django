from django.contrib import admin
from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'size', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'total', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'full_name')
    inlines = [OrderItemInline]
