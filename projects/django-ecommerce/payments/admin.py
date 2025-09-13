from django.contrib import admin
from .models import Payment, Refund, PaymentMethod, WebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'payment_method', 'status', 'amount', 'currency',
        'transaction_id', 'last_four_digits', 'brand', 'processed_at', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('order__order_number', 'transaction_id', 'payment_intent_id', 'charge_id')
    readonly_fields = ('created_at', 'updated_at', 'processed_at')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'payment_method', 'status', 'amount', 'currency')
        }),
        ('Stripe Information', {
            'fields': ('transaction_id', 'payment_intent_id', 'charge_id')
        }),
        ('Card Information', {
            'fields': ('last_four_digits', 'brand', 'expiry_month', 'expiry_year')
        }),
        ('Error Information', {
            'fields': ('error_message', 'error_code'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'payment', 'refund_id', 'amount', 'reason', 'status',
        'processed_at', 'created_at'
    )
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('refund_id', 'payment__order__order_number')
    readonly_fields = ('refund_id', 'created_at', 'updated_at', 'processed_at')
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('payment', 'refund_id', 'amount', 'reason', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment__order')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'payment_type', 'is_default', 'last_four_digits',
        'brand', 'expiry_month', 'expiry_year', 'created_at'
    )
    list_filter = ('payment_type', 'is_default', 'brand', 'created_at')
    search_fields = ('user__email', 'external_id', 'last_four_digits')
    readonly_fields = ('external_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Method Information', {
            'fields': ('user', 'payment_type', 'is_default')
        }),
        ('Card Information', {
            'fields': ('last_four_digits', 'brand', 'expiry_month', 'expiry_year')
        }),
        ('External Information', {
            'fields': ('external_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'event_id', 'event_type', 'processed', 'created_at'
    )
    list_filter = ('event_type', 'processed', 'created_at')
    search_fields = ('event_id', 'event_type')
    readonly_fields = ('event_id', 'data', 'created_at')
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_id', 'event_type', 'processed')
        }),
        ('Event Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )