"""
Admin configuration for cart app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Cart, CartItem, Wishlist


class CartItemInline(admin.TabularInline):
    """
    Inline admin for cart items.
    """
    model = CartItem
    extra = 0
    fields = ('product', 'variant', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('unit_price', 'total_price')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Cart admin.
    """
    list_display = ('user', 'session_key', 'total_items', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'session_key')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = _('Total Items')
    
    def total_price(self, obj):
        return f"${obj.total_price:.2f}"
    total_price.short_description = _('Total Price')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Cart Item admin.
    """
    list_display = ('cart', 'product', 'variant', 'quantity', 'unit_price', 'total_price')
    list_filter = ('created_at', 'product__category')
    search_fields = ('cart__user__email', 'product__name', 'variant__name')
    readonly_fields = ('unit_price', 'total_price', 'created_at', 'updated_at')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """
    Wishlist admin.
    """
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at', 'product__category')
    search_fields = ('user__email', 'product__name')
    readonly_fields = ('created_at',)