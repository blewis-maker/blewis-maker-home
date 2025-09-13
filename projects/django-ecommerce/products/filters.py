"""
Filters for the products app.
"""

import django_filters
from django.db.models import Q, Avg
from .models import Product, Brand, Category


class ProductFilter(django_filters.FilterSet):
    """
    Filter for Product model.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.filter(is_active=True))
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'brand', 'category', 'min_price', 'max_price', 'min_rating', 'in_stock', 'is_featured']
    
    def filter_min_rating(self, queryset, name, value):
        """
        Filter products by minimum average rating.
        """
        return queryset.annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
        ).filter(avg_rating__gte=value)
    
    def filter_in_stock(self, queryset, name, value):
        """
        Filter products by stock availability.
        """
        if value:
            return queryset.filter(
                variants__stock_quantity__gt=0,
                variants__is_active=True
            ).distinct()
        return queryset


class BrandFilter(django_filters.FilterSet):
    """
    Filter for Brand model.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Brand
        fields = ['name', 'description']


class CategoryFilter(django_filters.FilterSet):
    """
    Filter for Category model.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    parent = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
