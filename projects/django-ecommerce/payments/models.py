"""
Payment models for the e-commerce platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Payment(models.Model):
    """
    Payment model.
    """
    PAYMENT_METHODS = [
        ('stripe', _('Credit Card (Stripe)')),
        ('paypal', _('PayPal')),
        ('bank_transfer', _('Bank Transfer')),
        ('cash_on_delivery', _('Cash on Delivery')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    ]

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment'
    )
    payment_method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PAYMENT_METHODS
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    
    # External payment provider information
    transaction_id = models.CharField(_('transaction ID'), max_length=100, blank=True)
    payment_intent_id = models.CharField(_('payment intent ID'), max_length=100, blank=True)
    charge_id = models.CharField(_('charge ID'), max_length=100, blank=True)
    
    # Payment details
    last_four_digits = models.CharField(_('last four digits'), max_length=4, blank=True)
    brand = models.CharField(_('brand'), max_length=20, blank=True)
    expiry_month = models.CharField(_('expiry month'), max_length=2, blank=True)
    expiry_year = models.CharField(_('expiry year'), max_length=4, blank=True)
    
    # Error information
    error_message = models.TextField(_('error message'), blank=True)
    error_code = models.CharField(_('error code'), max_length=50, blank=True)
    
    # Timestamps
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"

    @property
    def is_successful(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status in ['failed', 'cancelled']

    @property
    def is_pending(self):
        return self.status in ['pending', 'processing']


class Refund(models.Model):
    """
    Refund model.
    """
    REFUND_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]

    REFUND_REASONS = [
        ('customer_request', _('Customer Request')),
        ('defective_product', _('Defective Product')),
        ('wrong_item', _('Wrong Item')),
        ('not_as_described', _('Not as Described')),
        ('duplicate_order', _('Duplicate Order')),
        ('fraudulent', _('Fraudulent')),
        ('other', _('Other')),
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    refund_id = models.CharField(_('refund ID'), max_length=100, unique=True)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    reason = models.CharField(
        _('reason'),
        max_length=20,
        choices=REFUND_REASONS,
        default='customer_request'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(_('notes'), blank=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Refund')
        verbose_name_plural = _('Refunds')
        db_table = 'refunds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount}"

    @property
    def is_successful(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status in ['failed', 'cancelled']


class PaymentMethod(models.Model):
    """
    Saved payment method model for customers.
    """
    PAYMENT_TYPES = [
        ('card', _('Credit/Debit Card')),
        ('bank_account', _('Bank Account')),
        ('paypal', _('PayPal')),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    payment_type = models.CharField(
        _('payment type'),
        max_length=20,
        choices=PAYMENT_TYPES
    )
    is_default = models.BooleanField(_('default'), default=False)
    
    # Card information
    last_four_digits = models.CharField(_('last four digits'), max_length=4, blank=True)
    brand = models.CharField(_('brand'), max_length=20, blank=True)
    expiry_month = models.CharField(_('expiry month'), max_length=2, blank=True)
    expiry_year = models.CharField(_('expiry year'), max_length=4, blank=True)
    
    # External provider information
    external_id = models.CharField(_('external ID'), max_length=100, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        db_table = 'payment_methods'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        if self.payment_type == 'card':
            return f"{self.brand} ****{self.last_four_digits}"
        return f"{self.get_payment_type_display()}"

    def save(self, *args, **kwargs):
        # Ensure only one default payment method per user
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class WebhookEvent(models.Model):
    """
    Webhook event model for tracking external payment events.
    """
    EVENT_TYPES = [
        ('payment_intent.succeeded', _('Payment Intent Succeeded')),
        ('payment_intent.payment_failed', _('Payment Intent Failed')),
        ('charge.succeeded', _('Charge Succeeded')),
        ('charge.failed', _('Charge Failed')),
        ('charge.dispute.created', _('Dispute Created')),
        ('invoice.payment_succeeded', _('Invoice Payment Succeeded')),
        ('invoice.payment_failed', _('Invoice Payment Failed')),
    ]

    event_id = models.CharField(_('event ID'), max_length=100, unique=True)
    event_type = models.CharField(
        _('event type'),
        max_length=50,
        choices=EVENT_TYPES
    )
    data = models.JSONField(_('event data'))
    processed = models.BooleanField(_('processed'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Webhook Event')
        verbose_name_plural = _('Webhook Events')
        db_table = 'webhook_events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.event_id}"