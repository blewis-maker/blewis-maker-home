"""
Admin configuration for payments app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Payment, Refund, PaymentMethod, WebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Payment admin.
    """
    list_display = (
        'order', 'payment_method', 'status', 'amount', 'currency',
        'transaction_id', 'processed_at', 'created_at'
    )
    list_filter = ('payment_method', 'status', 'currency', 'created_at')
    search_fields = (
        'order__order_number', 'transaction_id', 'payment_intent_id',
        'charge_id', 'last_four_digits'
    )
    readonly_fields = ('created_at', 'updated_at', 'processed_at')
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('order', 'payment_method', 'status', 'amount', 'currency')
        }),
        (_('External Provider'), {
            'fields': ('transaction_id', 'payment_intent_id', 'charge_id')
        }),
        (_('Card Details'), {
            'fields': ('last_four_digits', 'brand', 'expiry_month', 'expiry_year')
        }),
        (_('Error Information'), {
            'fields': ('error_message', 'error_code')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'processed_at')
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """
    Refund admin.
    """
    list_display = (
        'payment', 'refund_id', 'amount', 'reason', 'status',
        'processed_at', 'created_at'
    )
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('refund_id', 'payment__order__order_number', 'notes')
    readonly_fields = ('refund_id', 'created_at', 'updated_at', 'processed_at')
    
    fieldsets = (
        (_('Refund Information'), {
            'fields': ('payment', 'refund_id', 'amount', 'reason', 'status')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'processed_at')
        }),
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    Payment Method admin.
    """
    list_display = (
        'user', 'payment_type', 'last_four_digits', 'brand',
        'is_default', 'created_at'
    )
    list_filter = ('payment_type', 'is_default', 'created_at')
    search_fields = ('user__email', 'last_four_digits', 'external_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Payment Method'), {
            'fields': ('user', 'payment_type', 'is_default')
        }),
        (_('Card Information'), {
            'fields': ('last_four_digits', 'brand', 'expiry_month', 'expiry_year')
        }),
        (_('External Provider'), {
            'fields': ('external_id',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """
    Webhook Event admin.
    """
    list_display = ('event_id', 'event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed', 'created_at')
    search_fields = ('event_id', 'event_type')
    readonly_fields = ('event_id', 'data', 'created_at')
    
    fieldsets = (
        (_('Event Information'), {
            'fields': ('event_id', 'event_type', 'processed')
        }),
        (_('Event Data'), {
            'fields': ('data',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at',)
        }),
    )