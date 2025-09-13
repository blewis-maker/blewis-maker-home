"""
API views for payment management.
"""

import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Payment, Refund, PaymentMethod, WebhookEvent
from .serializers import (
    PaymentSerializer, CreatePaymentSerializer, PaymentMethodSerializer,
    RefundSerializer, CreateRefundSerializer, PaymentIntentSerializer
)
from orders.models import Order

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class PaymentListView(generics.ListAPIView):
    """
    List user's payments.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).select_related('order')


class PaymentDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific payment.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).select_related('order')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_intent(request, order_id):
    """
    Create a Stripe Payment Intent for an order.
    """
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if payment already exists
        if hasattr(order, 'payment'):
            return Response(
                {'detail': 'Payment already exists for this order.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create payment intent with Stripe
        intent_data = {
            'amount': int(order.total_amount * 100),  # Convert to cents
            'currency': serializer.validated_data['currency'].lower(),
            'metadata': {
                'order_id': order.id,
                'order_number': order.order_number,
                'user_id': request.user.id,
            }
        }

        if serializer.validated_data.get('payment_method_id'):
            intent_data['payment_method'] = serializer.validated_data['payment_method_id']
            intent_data['confirmation_method'] = 'manual'
            intent_data['confirm'] = True

        if serializer.validated_data.get('save_payment_method'):
            intent_data['setup_future_usage'] = 'off_session'

        if serializer.validated_data.get('return_url'):
            intent_data['return_url'] = serializer.validated_data['return_url']

        payment_intent = stripe.PaymentIntent.create(**intent_data)

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            payment_method='stripe',
            amount=order.total_amount,
            currency=serializer.validated_data['currency'],
            payment_intent_id=payment_intent.id,
            status='pending'
        )

        return Response({
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'payment': PaymentSerializer(payment).data
        })

    except stripe.error.StripeError as e:
        return Response(
            {'detail': f'Stripe error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'detail': f'Error creating payment intent: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request, payment_id):
    """
    Confirm a payment intent.
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
        
        if payment.status != 'pending':
            return Response(
                {'detail': 'Payment is not in pending status.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve and confirm the payment intent
        payment_intent = stripe.PaymentIntent.retrieve(payment.payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            payment.status = 'completed'
            payment.processed_at = timezone.now()
            payment.save()
            
            # Update order payment status
            payment.order.payment_status = 'paid'
            payment.order.save()
            
            return Response({
                'status': 'success',
                'payment': PaymentSerializer(payment).data
            })
        elif payment_intent.status == 'requires_action':
            return Response({
                'status': 'requires_action',
                'client_secret': payment_intent.client_secret
            })
        else:
            payment.status = 'failed'
            payment.error_message = f"Payment failed with status: {payment_intent.status}"
            payment.save()
            
            return Response({
                'status': 'failed',
                'error': payment.error_message
            }, status=status.HTTP_400_BAD_REQUEST)

    except stripe.error.StripeError as e:
        return Response(
            {'detail': f'Stripe error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'detail': f'Error confirming payment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class RefundListView(generics.ListCreateAPIView):
    """
    List and create refunds.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateRefundSerializer
        return RefundSerializer

    def get_queryset(self):
        return Refund.objects.filter(payment__order__user=self.request.user).select_related('payment__order')

    def create(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
        
        serializer = CreateRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                # Create refund with Stripe
                refund = stripe.Refund.create(
                    payment_intent=payment.payment_intent_id,
                    amount=int(serializer.validated_data['amount'] * 100),
                    reason=serializer.validated_data['reason']
                )

                # Create refund record
                refund_obj = Refund.objects.create(
                    payment=payment,
                    refund_id=refund.id,
                    amount=serializer.validated_data['amount'],
                    reason=serializer.validated_data['reason'],
                    notes=serializer.validated_data.get('notes', ''),
                    status='completed' if refund.status == 'succeeded' else 'pending'
                )

                return Response(
                    RefundSerializer(refund_obj).data,
                    status=status.HTTP_201_CREATED
                )

        except stripe.error.StripeError as e:
            return Response(
                {'detail': f'Stripe error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': f'Error creating refund: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentMethodListView(generics.ListCreateAPIView):
    """
    List and manage user's payment methods.
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_methods(request):
    """
    Get user's payment methods.
    """
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    serializer = PaymentMethodSerializer(payment_methods, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_method(request):
    """
    Create a new payment method.
    """
    try:
        # Create payment method with Stripe
        payment_method = stripe.PaymentMethod.create(
            type='card',
            card={
                'number': request.data.get('card_number'),
                'exp_month': request.data.get('exp_month'),
                'exp_year': request.data.get('exp_year'),
                'cvc': request.data.get('cvc'),
            }
        )

        # Attach to customer
        customer = stripe.Customer.create(
            email=request.user.email,
            name=f"{request.user.first_name} {request.user.last_name}".strip()
        )

        stripe.PaymentMethod.attach(
            payment_method.id,
            customer=customer.id
        )

        # Create payment method record
        pm = PaymentMethod.objects.create(
            user=request.user,
            payment_type='card',
            external_id=payment_method.id,
            last_four_digits=payment_method.card.last4,
            brand=payment_method.card.brand,
            expiry_month=str(payment_method.card.exp_month),
            expiry_year=str(payment_method.card.exp_year),
            is_default=not PaymentMethod.objects.filter(user=request.user).exists()
        )

        return Response(PaymentMethodSerializer(pm).data, status=status.HTTP_201_CREATED)

    except stripe.error.StripeError as e:
        return Response(
            {'detail': f'Stripe error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'detail': f'Error creating payment method: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Create webhook event record
    webhook_event, created = WebhookEvent.objects.get_or_create(
        event_id=event['id'],
        defaults={
            'event_type': event['type'],
            'data': event['data']
        }
    )

    if not created:
        return HttpResponse(status=200)  # Already processed

    # Process the event
    try:
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment = Payment.objects.get(payment_intent_id=payment_intent['id'])
            payment.status = 'completed'
            payment.processed_at = timezone.now()
            payment.save()
            
            # Update order status
            payment.order.payment_status = 'paid'
            payment.order.save()

        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            payment = Payment.objects.get(payment_intent_id=payment_intent['id'])
            payment.status = 'failed'
            payment.error_message = payment_intent.get('last_payment_error', {}).get('message', '')
            payment.save()

        webhook_event.processed = True
        webhook_event.save()

    except Exception as e:
        # Log the error but don't fail the webhook
        print(f"Error processing webhook: {str(e)}")

    return HttpResponse(status=200)