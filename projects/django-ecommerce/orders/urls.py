from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order management
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    
    # Order utilities
    path('stats/', views.order_stats, name='order_stats'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
    
    # Coupons
    path('coupons/', views.CouponListView.as_view(), name='coupon_list'),
]