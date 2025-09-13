"""
URL configuration for the cart app.
"""

from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart management
    path('', views.CartView.as_view(), name='cart_detail'),
    path('items/', views.CartItemListView.as_view(), name='cart_items'),
    path('items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart_item_detail'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('items/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('summary/', views.cart_summary, name='cart_summary'),
    
    # Wishlist management
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', views.WishlistDetailView.as_view(), name='wishlist_detail'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
