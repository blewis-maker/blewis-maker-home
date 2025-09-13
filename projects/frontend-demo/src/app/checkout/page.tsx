'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import Layout from '../../components/Layout';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { 
  CreditCardIcon,
  TruckIcon,
  ShieldCheckIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { useCart } from '../../contexts/CartContext';
import { useAuth } from '../../contexts/AuthContext';
import { formatPrice } from '../../lib/utils';
import api from '../../lib/api';
import toast from 'react-hot-toast';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

const checkoutSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  address_line_1: z.string().min(1, 'Address is required'),
  address_line_2: z.string().optional(),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(1, 'State is required'),
  postal_code: z.string().min(1, 'Postal code is required'),
  country: z.string().min(1, 'Country is required'),
  phone: z.string().min(10, 'Phone number is required'),
});

type CheckoutForm = z.infer<typeof checkoutSchema>;

function CheckoutForm() {
  const router = useRouter();
  const { cart, clearCart } = useCart();
  const { user } = useAuth();
  const stripe = useStripe();
  const elements = useElements();
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [step, setStep] = useState(1);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<CheckoutForm>({
    resolver: zodResolver(checkoutSchema),
  });

  // Pre-fill form with user data
  useEffect(() => {
    if (user) {
      setValue('email', user.email);
      setValue('first_name', user.first_name || '');
      setValue('last_name', user.last_name || '');
    }
  }, [user, setValue]);

  const onSubmit = async (data: CheckoutForm) => {
    if (!stripe || !elements || !cart) return;

    try {
      setIsProcessing(true);

      // Create payment intent
      const paymentIntentResponse = await api.post('/payments/create-payment-intent/', {
        amount: Math.round(cart.total_amount * 100), // Convert to cents
        currency: 'usd',
      });

      const { client_secret } = paymentIntentResponse.data;

      // Confirm payment
      const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: elements.getElement(CardElement)!,
          billing_details: {
            name: `${data.first_name} ${data.last_name}`,
            email: data.email,
            phone: data.phone,
            address: {
              line1: data.address_line_1,
              line2: data.address_line_2,
              city: data.city,
              state: data.state,
              postal_code: data.postal_code,
              country: data.country,
            },
          },
        },
      });

      if (error) {
        toast.error(error.message || 'Payment failed');
        return;
      }

      if (paymentIntent.status === 'succeeded') {
        // Create order
        const orderResponse = await api.post('/orders/', {
          shipping_address: {
            first_name: data.first_name,
            last_name: data.last_name,
            address_line_1: data.address_line_1,
            address_line_2: data.address_line_2,
            city: data.city,
            state: data.state,
            postal_code: data.postal_code,
            country: data.country,
            phone: data.phone,
          },
          payment_intent_id: paymentIntent.id,
        });

        // Clear cart
        await clearCart();
        
        toast.success('Order placed successfully!');
        router.push(`/orders/${orderResponse.data.id}`);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Checkout failed');
    } finally {
      setIsProcessing(false);
    }
  };

  if (!cart || cart.items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Your cart is empty</p>
        <Button onClick={() => router.push('/products')} className="mt-4">
          Continue Shopping
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      {/* Step 1: Shipping Information */}
      {step === 1 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Shipping Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Email"
              type="email"
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              label="Phone"
              type="tel"
              error={errors.phone?.message}
              {...register('phone')}
            />
            <Input
              label="First Name"
              type="text"
              error={errors.first_name?.message}
              {...register('first_name')}
            />
            <Input
              label="Last Name"
              type="text"
              error={errors.last_name?.message}
              {...register('last_name')}
            />
            <Input
              label="Address Line 1"
              type="text"
              error={errors.address_line_1?.message}
              {...register('address_line_1')}
            />
            <Input
              label="Address Line 2 (Optional)"
              type="text"
              error={errors.address_line_2?.message}
              {...register('address_line_2')}
            />
            <Input
              label="City"
              type="text"
              error={errors.city?.message}
              {...register('city')}
            />
            <Input
              label="State"
              type="text"
              error={errors.state?.message}
              {...register('state')}
            />
            <Input
              label="Postal Code"
              type="text"
              error={errors.postal_code?.message}
              {...register('postal_code')}
            />
            <Input
              label="Country"
              type="text"
              error={errors.country?.message}
              {...register('country')}
            />
          </div>

          <div className="flex justify-end mt-6">
            <Button type="button" onClick={() => setStep(2)}>
              Continue to Payment
            </Button>
          </div>
        </div>
      )}

      {/* Step 2: Payment */}
      {step === 2 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Payment Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Card Details
              </label>
              <div className="border border-gray-300 rounded-md p-3">
                <CardElement
                  options={{
                    style: {
                      base: {
                        fontSize: '16px',
                        color: '#424770',
                        '::placeholder': {
                          color: '#aab7c4',
                        },
                      },
                    },
                  }}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-between mt-6">
            <Button type="button" variant="outline" onClick={() => setStep(1)}>
              Back to Shipping
            </Button>
            <Button type="submit" isLoading={isProcessing} disabled={isProcessing}>
              {isProcessing ? <LoadingSpinner /> : 'Complete Order'}
            </Button>
          </div>
        </div>
      )}
    </form>
  );
}

export default function CheckoutPage() {
  const router = useRouter();
  const { cart } = useCart();
  const { isAuthenticated } = useAuth();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner />
        </div>
      </Layout>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <p className="text-gray-600">Your cart is empty</p>
            <Button onClick={() => router.push('/products')} className="mt-4">
              Continue Shopping
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Checkout Form */}
          <div className="lg:col-span-2">
            <Elements stripe={stripePromise}>
              <CheckoutForm />
            </Elements>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-8">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>
              
              {/* Cart Items */}
              <div className="space-y-3 mb-6">
                {cart.items.map((item) => (
                  <div key={item.id} className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg overflow-hidden">
                      {item.product.primary_image ? (
                        <img
                          src={item.product.primary_image}
                          alt={item.product.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                          No image
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.product.name}
                      </p>
                      <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                    </div>
                    <p className="text-sm font-medium text-gray-900">
                      {formatPrice(item.price * item.quantity)}
                    </p>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="text-gray-900">{formatPrice(cart.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Shipping</span>
                  <span className="text-gray-900">
                    {cart.shipping_amount > 0 ? formatPrice(cart.shipping_amount) : 'Free'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax</span>
                  <span className="text-gray-900">{formatPrice(cart.tax_amount)}</span>
                </div>
                {cart.discount_amount > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Discount</span>
                    <span>-{formatPrice(cart.discount_amount)}</span>
                  </div>
                )}
                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between text-lg font-medium">
                    <span className="text-gray-900">Total</span>
                    <span className="text-gray-900">{formatPrice(cart.total_amount)}</span>
                  </div>
                </div>
              </div>

              {/* Security Features */}
              <div className="space-y-3 text-sm text-gray-500">
                <div className="flex items-center space-x-2">
                  <ShieldCheckIcon className="h-4 w-4" />
                  <span>Secure payment processing</span>
                </div>
                <div className="flex items-center space-x-2">
                  <TruckIcon className="h-4 w-4" />
                  <span>Free shipping on orders over $50</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircleIcon className="h-4 w-4" />
                  <span>30-day return policy</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
