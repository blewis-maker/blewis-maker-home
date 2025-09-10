"""
Order models for the e-commerce platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class Order(models.Model):
    """
    Order model.
    """
    ORDER_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(_('order number'), max_length=20, unique=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Pricing
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(_('shipping amount'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    
    # Customer information
    billing_first_name = models.CharField(_('billing first name'), max_length=150)
    billing_last_name = models.CharField(_('billing last name'), max_length=150)
    billing_company = models.CharField(_('billing company'), max_length=100, blank=True)
    billing_address_line_1 = models.CharField(_('billing address line 1'), max_length=255)
    billing_address_line_2 = models.CharField(_('billing address line 2'), max_length=255, blank=True)
    billing_city = models.CharField(_('billing city'), max_length=100)
    billing_state = models.CharField(_('billing state'), max_length=100)
    billing_postal_code = models.CharField(_('billing postal code'), max_length=20)
    billing_country = models.CharField(_('billing country'), max_length=100)
    billing_phone = models.CharField(_('billing phone'), max_length=20, blank=True)
    
    shipping_first_name = models.CharField(_('shipping first name'), max_length=150)
    shipping_last_name = models.CharField(_('shipping last name'), max_length=150)
    shipping_company = models.CharField(_('shipping company'), max_length=100, blank=True)
    shipping_address_line_1 = models.CharField(_('shipping address line 1'), max_length=255)
    shipping_address_line_2 = models.CharField(_('shipping address line 2'), max_length=255, blank=True)
    shipping_city = models.CharField(_('shipping city'), max_length=100)
    shipping_state = models.CharField(_('shipping state'), max_length=100)
    shipping_postal_code = models.CharField(_('shipping postal code'), max_length=20)
    shipping_country = models.CharField(_('shipping country'), max_length=100)
    shipping_phone = models.CharField(_('shipping phone'), max_length=20, blank=True)
    
    # Additional information
    notes = models.TextField(_('notes'), blank=True)
    tracking_number = models.CharField(_('tracking number'), max_length=100, blank=True)
    shipped_at = models.DateTimeField(_('shipped at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """
        Generate a unique order number.
        """
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    @property
    def billing_full_name(self):
        return f"{self.billing_first_name} {self.billing_last_name}".strip()

    @property
    def shipping_full_name(self):
        return f"{self.shipping_first_name} {self.shipping_last_name}".strip()

    @property
    def is_paid(self):
        return self.payment_status == 'paid'

    @property
    def is_shipped(self):
        return self.status in ['shipped', 'delivered']

    @property
    def is_delivered(self):
        return self.status == 'delivered'

    @property
    def is_cancelled(self):
        return self.status == 'cancelled'


class OrderItem(models.Model):
    """
    Order item model.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('total price'), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        db_table = 'order_items'

    def __str__(self):
        variant_text = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_text} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """
    Order status history model for tracking status changes.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(_('status'), max_length=20)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        db_table = 'order_status_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class Coupon(models.Model):
    """
    Coupon model for discounts.
    """
    COUPON_TYPES = [
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    ]

    code = models.CharField(_('code'), max_length=50, unique=True)
    description = models.CharField(_('description'), max_length=200)
    coupon_type = models.CharField(
        _('coupon type'),
        max_length=20,
        choices=COUPON_TYPES,
        default='percentage'
    )
    value = models.DecimalField(_('value'), max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(
        _('minimum amount'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    maximum_discount = models.DecimalField(
        _('maximum discount'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    usage_limit = models.PositiveIntegerField(_('usage limit'), null=True, blank=True)
    used_count = models.PositiveIntegerField(_('used count'), default=0)
    is_active = models.BooleanField(_('active'), default=True)
    valid_from = models.DateTimeField(_('valid from'))
    valid_until = models.DateTimeField(_('valid until'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        db_table = 'coupons'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def calculate_discount(self, amount):
        """
        Calculate discount amount for given order amount.
        """
        if not self.is_valid or (self.minimum_amount and amount < self.minimum_amount):
            return Decimal('0')

        if self.coupon_type == 'percentage':
            discount = amount * (self.value / 100)
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:  # fixed
            discount = self.value

        return min(discount, amount)