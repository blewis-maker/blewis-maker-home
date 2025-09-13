"""
URL configuration for the products app.
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Brands
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brands/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Products
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Product Images
    path('<int:product_id>/images/', views.ProductImageView.as_view(), name='product_images'),
    
    # Product Variants
    path('<int:product_id>/variants/', views.ProductVariantView.as_view(), name='product_variants'),
    
    # Product Reviews
    path('<int:product_id>/reviews/', views.ProductReviewView.as_view(), name='product_reviews'),
    
    # Special product collections
    path('featured/', views.featured_products_view, name='featured_products'),
    path('new/', views.new_products_view, name='new_products'),
    path('best-selling/', views.best_selling_products_view, name='best_selling_products'),
    path('stats/', views.product_stats_view, name='product_stats'),
]
