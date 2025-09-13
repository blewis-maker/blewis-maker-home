"""
Order serializers for the e-commerce platform.
"""

from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, Coupon
from products.serializers import ProductListSerializer, ProductVariantSerializer
from accounts.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'quantity', 'unit_price', 'total_price', 'created_at'
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'created_at', 'created_by_name']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    billing_full_name = serializers.CharField(read_only=True)
    shipping_full_name = serializers.CharField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    is_shipped = serializers.BooleanField(read_only=True)
    is_delivered = serializers.BooleanField(read_only=True)
    is_cancelled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'subtotal', 'tax_amount',
            'shipping_amount', 'discount_amount', 'total_amount', 'billing_first_name',
            'billing_last_name', 'billing_company', 'billing_address_line_1',
            'billing_address_line_2', 'billing_city', 'billing_state', 'billing_postal_code',
            'billing_country', 'billing_phone', 'shipping_first_name', 'shipping_last_name',
            'shipping_company', 'shipping_address_line_1', 'shipping_address_line_2',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'shipping_phone', 'notes', 'tracking_number', 'shipped_at', 'delivered_at',
            'created_at', 'updated_at', 'items', 'status_history', 'billing_full_name',
            'shipping_full_name', 'is_paid', 'is_shipped', 'is_delivered', 'is_cancelled'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    billing_full_name = serializers.CharField(read_only=True)
    shipping_full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'total_amount',
            'billing_full_name', 'shipping_full_name', 'items_count', 'created_at'
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer for creating a new order from cart.
    """
    # Billing information
    billing_first_name = serializers.CharField(max_length=150)
    billing_last_name = serializers.CharField(max_length=150)
    billing_company = serializers.CharField(max_length=100, required=False, allow_blank=True)
    billing_address_line_1 = serializers.CharField(max_length=255)
    billing_address_line_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    billing_city = serializers.CharField(max_length=100)
    billing_state = serializers.CharField(max_length=100)
    billing_postal_code = serializers.CharField(max_length=20)
    billing_country = serializers.CharField(max_length=100)
    billing_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Shipping information
    shipping_first_name = serializers.CharField(max_length=150)
    shipping_last_name = serializers.CharField(max_length=150)
    shipping_company = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shipping_address_line_1 = serializers.CharField(max_length=255)
    shipping_address_line_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100)
    shipping_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Additional information
    notes = serializers.CharField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_coupon_code(self, value):
        if value:
            try:
                coupon = Coupon.objects.get(code=value)
                if not coupon.is_valid:
                    raise serializers.ValidationError("Invalid or expired coupon.")
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Coupon not found.")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    """
    Serializer for updating order status.
    """
    status = serializers.ChoiceField(choices=Order.ORDER_STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    tracking_number = serializers.CharField(max_length=100, required=False, allow_blank=True)


class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'coupon_type', 'value', 'minimum_amount',
            'maximum_discount', 'usage_limit', 'used_count', 'is_active', 'valid_from',
            'valid_until', 'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['used_count', 'created_at', 'updated_at']


class ValidateCouponSerializer(serializers.Serializer):
    """
    Serializer for validating coupon codes.
    """
    coupon_code = serializers.CharField(max_length=50)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_coupon_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
            if not coupon.is_valid:
                raise serializers.ValidationError("Invalid or expired coupon.")
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Coupon not found.")
        return value

    def validate(self, data):
        coupon_code = data.get('coupon_code')
        order_amount = data.get('order_amount')

        if coupon_code and order_amount:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.minimum_amount and order_amount < coupon.minimum_amount:
                    raise serializers.ValidationError(
                        f"Minimum order amount of ${coupon.minimum_amount} required for this coupon."
                    )
            except Coupon.DoesNotExist:
                pass

        return data
