"""
Payment serializers for the e-commerce platform.
"""

from rest_framework import serializers
from .models import Payment, Refund, PaymentMethod, WebhookEvent
from orders.serializers import OrderSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'status', 'amount', 'currency',
            'transaction_id', 'payment_intent_id', 'charge_id', 'last_four_digits',
            'brand', 'expiry_month', 'expiry_year', 'error_message', 'error_code',
            'processed_at', 'created_at', 'updated_at', 'is_successful', 'is_failed', 'is_pending'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CreatePaymentSerializer(serializers.Serializer):
    """
    Serializer for creating a payment intent.
    """
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHODS)
    save_payment_method = serializers.BooleanField(default=False)

    def validate_payment_method(self, value):
        # For now, only support Stripe
        if value != 'stripe':
            raise serializers.ValidationError("Only Stripe payments are currently supported.")
        return value


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'payment_type', 'is_default', 'last_four_digits',
            'brand', 'expiry_month', 'expiry_year', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RefundSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'refund_id', 'amount', 'reason', 'status',
            'notes', 'processed_at', 'created_at', 'updated_at',
            'is_successful', 'is_failed'
        ]
        read_only_fields = ['refund_id', 'created_at', 'updated_at']


class CreateRefundSerializer(serializers.Serializer):
    """
    Serializer for creating a refund.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.ChoiceField(choices=Refund.REFUND_REASONS, default='customer_request')
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Refund amount must be greater than zero.")
        return value


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'event_id', 'event_type', 'data', 'processed', 'created_at'
        ]
        read_only_fields = ['created_at']


class PaymentIntentSerializer(serializers.Serializer):
    """
    Serializer for Stripe Payment Intent creation.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    payment_method_id = serializers.CharField(max_length=100, required=False)
    save_payment_method = serializers.BooleanField(default=False)
    return_url = serializers.URLField(required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_currency(self, value):
        supported_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
        if value.upper() not in supported_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(supported_currencies)}")
        return value.upper()
