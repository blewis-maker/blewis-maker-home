'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import Layout from '@/components/Layout';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { 
  TrashIcon,
  MinusIcon,
  PlusIcon,
  ShoppingBagIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { useCart } from '@/contexts/CartContext';
import { useAuth } from '@/contexts/AuthContext';
import { formatPrice } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function CartPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const { cart, updateQuantity, removeFromCart, clearCart, refreshCart } = useCart();
  const [isUpdating, setIsUpdating] = useState<number | null>(null);

  // Redirect if not authenticated
  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const handleQuantityChange = async (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    
    try {
      setIsUpdating(itemId);
      await updateQuantity(itemId, newQuantity);
    } catch (error: unknown) {
      toast.error('Failed to update quantity');
    } finally {
      setIsUpdating(null);
    }
  };

  const handleRemoveItem = async (itemId: number) => {
    try {
      await removeFromCart(itemId);
      toast.success('Item removed from cart');
    } catch (error: unknown) {
      toast.error('Failed to remove item');
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      try {
        await clearCart();
        toast.success('Cart cleared');
      } catch (error: unknown) {
        toast.error('Failed to clear cart');
      }
    }
  };

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
            <ShoppingBagIcon className="h-24 w-24 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
            <p className="text-gray-600 mb-8">Add some products to get started!</p>
            <Link href="/products">
              <Button size="lg">Continue Shopping</Button>
            </Link>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.back()}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              Back
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          </div>
          <Button variant="outline" onClick={handleClearCart}>
            Clear Cart
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">
                  Cart Items ({cart.total_items})
                </h2>
              </div>
              <div className="divide-y divide-gray-200">
                {cart.items.map((item) => (
                  <div key={item.id} className="p-6">
                    <div className="flex items-center space-x-4">
                      {/* Product Image */}
                      <div className="flex-shrink-0">
                        <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden">
                          {item.product.primary_image ? (
                            <Image
                              src={item.product.primary_image}
                              alt={item.product.name}
                              width={80}
                              height={80}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                              No image
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Product Info */}
                      <div className="flex-1 min-w-0">
                        <Link
                          href={`/products/${item.product.id}`}
                          className="text-lg font-medium text-gray-900 hover:text-blue-600"
                        >
                          {item.product.name}
                        </Link>
                        {item.variant && (
                          <p className="text-sm text-gray-600 mt-1">
                            {item.variant.name}
                          </p>
                        )}
                        <p className="text-lg font-medium text-gray-900 mt-2">
                          {formatPrice(item.price)}
                        </p>
                      </div>

                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center border border-gray-300 rounded-lg">
                          <button
                            onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                            disabled={item.quantity <= 1 || isUpdating === item.id}
                            className="p-2 hover:bg-gray-100 disabled:opacity-50"
                          >
                            <MinusIcon className="h-4 w-4" />
                          </button>
                          <span className="px-4 py-2 min-w-[3rem] text-center">
                            {isUpdating === item.id ? (
                              <LoadingSpinner />
                            ) : (
                              item.quantity
                            )}
                          </span>
                          <button
                            onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                            disabled={isUpdating === item.id}
                            className="p-2 hover:bg-gray-100 disabled:opacity-50"
                          >
                            <PlusIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </div>

                      {/* Remove Button */}
                      <button
                        onClick={() => handleRemoveItem(item.id)}
                        className="text-red-600 hover:text-red-800 p-2"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-8">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>
              
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

              <div className="space-y-3">
                <Link href="/checkout" className="block">
                  <Button className="w-full" size="lg">
                    Proceed to Checkout
                  </Button>
                </Link>
                <Link href="/products">
                  <Button variant="outline" className="w-full">
                    Continue Shopping
                  </Button>
                </Link>
              </div>

              {/* Security Badge */}
              <div className="mt-6 text-center">
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                  <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                  <span>Secure checkout</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
