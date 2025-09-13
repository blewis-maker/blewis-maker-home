"""
Cart admin configuration for the e-commerce platform.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Wishlist


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin interface for Cart model.
    """
    list_display = [
        'id', 'user', 'session_key', 'total_items', 'total_price',
        'created_at', 'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_price']
    ordering = ['-created_at']

    def total_items(self, obj):
        """Display total items in cart."""
        return obj.total_items
    total_items.short_description = 'Total Items'

    def total_price(self, obj):
        """Display total price of cart."""
        return f"${obj.total_price:.2f}"
    total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin interface for CartItem model.
    """
    list_display = [
        'id', 'cart', 'product', 'variant', 'quantity', 'unit_price',
        'total_price', 'created_at'
    ]
    list_filter = ['created_at', 'cart__user']
    search_fields = ['product__name', 'cart__user__email']
    readonly_fields = ['created_at', 'updated_at', 'unit_price', 'total_price']
    ordering = ['-created_at']

    def unit_price(self, obj):
        """Display unit price of item."""
        return f"${obj.unit_price:.2f}"
    unit_price.short_description = 'Unit Price'

    def total_price(self, obj):
        """Display total price of item."""
        return f"${obj.total_price:.2f}"
    total_price.short_description = 'Total Price'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """
    Admin interface for Wishlist model.
    """
    list_display = ['id', 'user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']