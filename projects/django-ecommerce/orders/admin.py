"""
Admin configuration for orders app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusHistory, Coupon


class OrderItemInline(admin.TabularInline):
    """
    Inline admin for order items.
    """
    model = OrderItem
    extra = 0
    fields = ('product', 'variant', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('unit_price', 'total_price')


class OrderStatusHistoryInline(admin.TabularInline):
    """
    Inline admin for order status history.
    """
    model = OrderStatusHistory
    extra = 0
    fields = ('status', 'notes', 'created_at', 'created_by')
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order admin.
    """
    list_display = (
        'order_number', 'user', 'status', 'payment_status', 
        'total_amount', 'created_at'
    )
    list_filter = (
        'status', 'payment_status', 'created_at', 'shipping_country'
    )
    search_fields = (
        'order_number', 'user__email', 'billing_first_name', 
        'billing_last_name', 'billing_city'
    )
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        (_('Pricing'), {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount')
        }),
        (_('Billing Address'), {
            'fields': (
                'billing_first_name', 'billing_last_name', 'billing_company',
                'billing_address_line_1', 'billing_address_line_2',
                'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
                'billing_phone'
            )
        }),
        (_('Shipping Address'), {
            'fields': (
                'shipping_first_name', 'shipping_last_name', 'shipping_company',
                'shipping_address_line_1', 'shipping_address_line_2',
                'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
                'shipping_phone'
            )
        }),
        (_('Additional Information'), {
            'fields': ('notes', 'tracking_number', 'shipped_at', 'delivered_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Order Item admin.
    """
    list_display = ('order', 'product', 'variant', 'quantity', 'unit_price', 'total_price')
    list_filter = ('created_at', 'product__category')
    search_fields = ('order__order_number', 'product__name', 'variant__name')
    readonly_fields = ('unit_price', 'total_price', 'created_at')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Order Status History admin.
    """
    list_display = ('order', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'notes')
    readonly_fields = ('created_at',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Coupon admin.
    """
    list_display = (
        'code', 'description', 'coupon_type', 'value', 
        'usage_limit', 'used_count', 'is_active', 'valid_until'
    )
    list_filter = ('coupon_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'description', 'coupon_type', 'value')
        }),
        (_('Conditions'), {
            'fields': ('minimum_amount', 'maximum_discount', 'usage_limit')
        }),
        (_('Validity'), {
            'fields': ('is_active', 'valid_from', 'valid_until')
        }),
        (_('Usage'), {
            'fields': ('used_count',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )