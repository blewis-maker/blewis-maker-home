"""
API views for order management.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem, OrderStatusHistory, Coupon
from .serializers import (
    OrderSerializer, OrderListSerializer, CreateOrderSerializer,
    UpdateOrderStatusSerializer, CouponSerializer, ValidateCouponSerializer
)
from cart.models import Cart, CartItem
from products.models import Product, ProductVariant


class OrderListView(generics.ListCreateAPIView):
    """
    List user's orders or create a new order from cart.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    def create(self, request, *args, **kwargs):
        """
        Create a new order from the user's cart.
        """
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'detail': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.items.exists():
            return Response(
                {'detail': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate cart items and stock
        cart_items = cart.items.all()
        for item in cart_items:
            if item.variant:
                if item.quantity > item.variant.stock_quantity:
                    return Response(
                        {'detail': f'Insufficient stock for {item.product.name} - {item.variant.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                if item.quantity > item.product.stock_quantity:
                    return Response(
                        {'detail': f'Insufficient stock for {item.product.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        try:
            with transaction.atomic():
                # Create order with default values first
                order_data = serializer.validated_data
                order = Order.objects.create(
                    user=request.user,
                    billing_first_name=order_data['billing_first_name'],
                    billing_last_name=order_data['billing_last_name'],
                    billing_company=order_data.get('billing_company', ''),
                    billing_address_line_1=order_data['billing_address_line_1'],
                    billing_address_line_2=order_data.get('billing_address_line_2', ''),
                    billing_city=order_data['billing_city'],
                    billing_state=order_data['billing_state'],
                    billing_postal_code=order_data['billing_postal_code'],
                    billing_country=order_data['billing_country'],
                    billing_phone=order_data.get('billing_phone', ''),
                    shipping_first_name=order_data['shipping_first_name'],
                    shipping_last_name=order_data['shipping_last_name'],
                    shipping_company=order_data.get('shipping_company', ''),
                    shipping_address_line_1=order_data['shipping_address_line_1'],
                    shipping_address_line_2=order_data.get('shipping_address_line_2', ''),
                    shipping_city=order_data['shipping_city'],
                    shipping_state=order_data['shipping_state'],
                    shipping_postal_code=order_data['shipping_postal_code'],
                    shipping_country=order_data['shipping_country'],
                    shipping_phone=order_data.get('shipping_phone', ''),
                    notes=order_data.get('notes', ''),
                    # Set default values for required fields
                    subtotal=Decimal('0'),
                    tax_amount=Decimal('0'),
                    shipping_amount=Decimal('0'),
                    discount_amount=Decimal('0'),
                    total_amount=Decimal('0'),
                )

                # Calculate pricing
                subtotal = Decimal('0')
                for item in cart_items:
                    unit_price = item.variant.price if item.variant else item.product.price
                    total_price = unit_price * item.quantity
                    subtotal += total_price

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        variant=item.variant,
                        quantity=item.quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                # Apply coupon if provided
                discount_amount = Decimal('0')
                if order_data.get('coupon_code'):
                    try:
                        coupon = Coupon.objects.get(code=order_data['coupon_code'])
                        if coupon.is_valid and (not coupon.minimum_amount or subtotal >= coupon.minimum_amount):
                            discount_amount = coupon.calculate_discount(subtotal)
                            coupon.used_count += 1
                            coupon.save()
                    except Coupon.DoesNotExist:
                        pass

                # Calculate final amounts (simplified - no tax/shipping for now)
                tax_amount = Decimal('0')
                shipping_amount = Decimal('0')
                total_amount = subtotal + tax_amount + shipping_amount - discount_amount

                # Update order with calculated amounts
                order.subtotal = subtotal
                order.tax_amount = tax_amount
                order.shipping_amount = shipping_amount
                order.discount_amount = discount_amount
                order.total_amount = total_amount
                order.save()

                # Update stock quantities
                for item in cart_items:
                    if item.variant:
                        item.variant.stock_quantity -= item.quantity
                        item.variant.save()
                    else:
                        item.product.stock_quantity -= item.quantity
                        item.product.save()

                # Clear cart
                cart.clear()

                # Create initial status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='pending',
                    notes='Order created',
                    created_by=request.user
                )

                return Response(
                    OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            return Response(
                {'detail': f'Error creating order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific order.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product', 'items__variant', 'status_history'
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    Update order status (admin only).
    """
    serializer_class = UpdateOrderStatusSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Order.objects.all()

    def perform_update(self, serializer):
        order = self.get_object()
        old_status = order.status
        new_status = serializer.validated_data['status']
        
        # Update order status
        order.status = new_status
        
        # Set timestamps for specific statuses
        if new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
            
        order.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=serializer.validated_data.get('notes', ''),
            created_by=self.request.user
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    """
    Validate a coupon code and calculate discount.
    """
    serializer = ValidateCouponSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    coupon_code = serializer.validated_data['coupon_code']
    order_amount = serializer.validated_data['order_amount']

    try:
        coupon = Coupon.objects.get(code=coupon_code)
        discount_amount = coupon.calculate_discount(order_amount)
        
        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data,
            'discount_amount': discount_amount,
            'final_amount': order_amount - discount_amount
        })
    except Coupon.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Coupon not found'
        })


class CouponListView(generics.ListAPIView):
    """
    List active coupons.
    """
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Coupon.objects.filter(is_active=True).filter(
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_stats(request):
    """
    Get order statistics for the user.
    """
    user_orders = Order.objects.filter(user=request.user)
    
    stats = {
        'total_orders': user_orders.count(),
        'pending_orders': user_orders.filter(status='pending').count(),
        'completed_orders': user_orders.filter(status='delivered').count(),
        'cancelled_orders': user_orders.filter(status='cancelled').count(),
        'total_spent': sum(order.total_amount for order in user_orders if order.is_paid),
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, pk):
    """
    Cancel an order (if it's still pending).
    """
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    if order.status != 'pending':
        return Response(
            {'detail': 'Only pending orders can be cancelled.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            # Update order status
            order.status = 'cancelled'
            order.save()
            
            # Restore stock quantities
            for item in order.items.all():
                if item.variant:
                    item.variant.stock_quantity += item.quantity
                    item.variant.save()
                else:
                    item.product.stock_quantity += item.quantity
                    item.product.save()
            
            # Create status history entry
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                notes='Order cancelled by customer',
                created_by=request.user
            )
            
            return Response({'detail': 'Order cancelled successfully.'})
            
    except Exception as e:
        return Response(
            {'detail': f'Error cancelling order: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )