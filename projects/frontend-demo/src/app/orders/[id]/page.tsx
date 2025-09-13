'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import Layout from '../../../components/Layout.tsx';
import Button from '../../../components/ui/Button.tsx';
import LoadingSpinner from '../../../components/ui/LoadingSpinner.tsx';
import { 
  ArrowLeftIcon,
  TruckIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  MapPinIcon,
  CreditCardIcon,
  PrinterIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../../../contexts/AuthContext.tsx';
import { formatPrice, formatDate, formatDateTime, getOrderStatusColor, getOrderStatusText } from '../../../lib/utils';
import api from '../../../lib/api';
import { Order } from '../../../types';

interface OrderDetailResponse {
  order: Order;
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'delivered':
      return <CheckCircleIcon className="h-6 w-6 text-green-600" />;
    case 'shipped':
      return <TruckIcon className="h-6 w-6 text-blue-600" />;
    case 'cancelled':
      return <XCircleIcon className="h-6 w-6 text-red-600" />;
    default:
      return <ClockIcon className="h-6 w-6 text-yellow-600" />;
  }
};

const getStatusDescription = (status: string) => {
  switch (status) {
    case 'pending':
      return 'Your order is being processed and will be confirmed soon.';
    case 'confirmed':
      return 'Your order has been confirmed and is being prepared for shipment.';
    case 'processing':
      return 'Your order is being processed and prepared for shipment.';
    case 'shipped':
      return 'Your order has been shipped and is on its way to you.';
    case 'delivered':
      return 'Your order has been delivered successfully.';
    case 'cancelled':
      return 'Your order has been cancelled.';
    case 'refunded':
      return 'Your order has been refunded.';
    default:
      return 'Order status unknown.';
  }
};

export default function OrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  
  const orderId = params.id as string;

  // Redirect if not authenticated
  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const { data: orderData, isLoading, error } = useQuery({
    queryKey: ['order', orderId],
    queryFn: async () => {
      const response = await api.get<OrderDetailResponse>(`/orders/${orderId}/`);
      return response.data;
    },
    enabled: !!orderId && isAuthenticated,
  });

  const order = orderData?.order;

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner />
        </div>
      </Layout>
    );
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner />
        </div>
      </Layout>
    );
  }

  if (error || !order) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-red-600">Order not found</p>
          <Button onClick={() => router.back()} className="mt-4">
            Go Back
          </Button>
        </div>
      </Layout>
    );
  }

  const handlePrint = () => {
    window.print();
  };

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
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Order #{order.order_number}
              </h1>
              <p className="text-gray-600">
                Placed on {formatDate(order.created_at)}
              </p>
            </div>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={handlePrint}>
              <PrinterIcon className="h-4 w-4 mr-2" />
              Print
            </Button>
            <Link href="/orders">
              <Button variant="outline">All Orders</Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Order Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Order Status */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-4 mb-4">
                {getStatusIcon(order.status)}
                <div>
                  <h2 className="text-lg font-medium text-gray-900">
                    {getOrderStatusText(order.status)}
                  </h2>
                  <p className="text-sm text-gray-600">
                    {getStatusDescription(order.status)}
                  </p>
                </div>
              </div>
              
              {/* Status Timeline */}
              <div className="space-y-3">
                {order.status_history?.map((history, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      index === 0 ? 'bg-blue-600' : 'bg-gray-300'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {getOrderStatusText(history.status)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatDateTime(history.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Order Items */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Order Items</h2>
              <div className="space-y-4">
                {order.items.map((item) => (
                  <div key={item.id} className="flex items-center space-x-4 py-4 border-b border-gray-200 last:border-b-0">
                    <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
                      {item.product.primary_image ? (
                        <Image
                          src={item.product.primary_image}
                          alt={item.product.name}
                          width={64}
                          height={64}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                          No image
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900">
                        {item.product.name}
                      </h3>
                      {item.variant && (
                        <p className="text-sm text-gray-500">{item.variant.name}</p>
                      )}
                      <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {formatPrice(item.price * item.quantity)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatPrice(item.price)} each
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Shipping Address */}
            {order.shipping_address && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Shipping Address</h2>
                <div className="flex items-start space-x-3">
                  <MapPinIcon className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {order.shipping_address.first_name} {order.shipping_address.last_name}
                    </p>
                    <p className="text-sm text-gray-600">
                      {order.shipping_address.address_line_1}
                    </p>
                    {order.shipping_address.address_line_2 && (
                      <p className="text-sm text-gray-600">
                        {order.shipping_address.address_line_2}
                      </p>
                    )}
                    <p className="text-sm text-gray-600">
                      {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.postal_code}
                    </p>
                    <p className="text-sm text-gray-600">
                      {order.shipping_address.country}
                    </p>
                    {order.shipping_address.phone && (
                      <p className="text-sm text-gray-600">
                        {order.shipping_address.phone}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-8">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="text-gray-900">{formatPrice(order.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Shipping</span>
                  <span className="text-gray-900">
                    {order.shipping_amount > 0 ? formatPrice(order.shipping_amount) : 'Free'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax</span>
                  <span className="text-gray-900">{formatPrice(order.tax_amount)}</span>
                </div>
                {order.discount_amount > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Discount</span>
                    <span>-{formatPrice(order.discount_amount)}</span>
                  </div>
                )}
                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between text-lg font-medium">
                    <span className="text-gray-900">Total</span>
                    <span className="text-gray-900">{formatPrice(order.total_amount)}</span>
                  </div>
                </div>
              </div>

              {/* Payment Information */}
              {order.payment && (
                <div className="border-t border-gray-200 pt-4 mb-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Payment Information</h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <CreditCardIcon className="h-4 w-4" />
                    <span>
                      {order.payment.payment_method?.brand?.toUpperCase()} •••• {order.payment.payment_method?.last4}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Paid on {formatDate(order.payment.created_at)}
                  </p>
                </div>
              )}

              {/* Order Actions */}
              <div className="space-y-3">
                {order.status === 'delivered' && (
                  <Button className="w-full">
                    Reorder Items
                  </Button>
                )}
                {order.status === 'pending' && (
                  <Button variant="outline" className="w-full">
                    Cancel Order
                  </Button>
                )}
                <Link href="/products" className="block">
                  <Button variant="outline" className="w-full">
                    Continue Shopping
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
