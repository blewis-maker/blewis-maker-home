"""
Admin configuration for products app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant, ProductReview
)


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for product images.
    """
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'sort_order')


class ProductVariantInline(admin.TabularInline):
    """
    Inline admin for product variants.
    """
    model = ProductVariant
    extra = 1
    fields = ('name', 'sku', 'price', 'stock_quantity', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin.
    """
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Brand admin.
    """
    list_display = ('name', 'website', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin.
    """
    list_display = (
        'name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 
        'is_active', 'is_featured', 'created_at'
    )
    list_filter = (
        'is_active', 'is_featured', 'is_digital', 'requires_shipping',
        'category', 'brand', 'created_at'
    )
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        (_('Pricing'), {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        (_('Classification'), {
            'fields': ('category', 'brand')
        }),
        (_('Physical Properties'), {
            'fields': ('weight', 'dimensions')
        }),
        (_('Inventory'), {
            'fields': ('stock_quantity', 'low_stock_threshold', 'track_inventory')
        }),
        (_('Settings'), {
            'fields': ('is_active', 'is_featured', 'is_digital', 'requires_shipping')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Product Image admin.
    """
    list_display = ('product', 'is_primary', 'sort_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    readonly_fields = ('created_at',)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Product Variant admin.
    """
    list_display = ('product', 'name', 'sku', 'price', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'product__category', 'created_at')
    search_fields = ('product__name', 'name', 'sku')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """
    Product Review admin.
    """
    list_display = ('product', 'user', 'rating', 'is_approved', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Review'), {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        (_('Status'), {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )