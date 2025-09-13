from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment management
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('orders/<int:order_id>/create-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('<int:payment_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    
    # Refunds
    path('refunds/', views.RefundListView.as_view(), name='refund_list'),
    
    # Payment methods
    path('methods/', views.payment_methods, name='payment_methods'),
    path('methods/create/', views.create_payment_method, name='create_payment_method'),
    
    # Webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]