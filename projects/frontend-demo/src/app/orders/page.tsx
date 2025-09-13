'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Layout from '@/components/Layout';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { 
  EyeIcon,
  TruckIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '@/contexts/AuthContext';
import { formatPrice, formatDate, getOrderStatusColor, getOrderStatusText } from '@/lib/utils';
import api from '@/lib/api';
import { Order } from '@/types';

interface OrdersResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Order[];
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'delivered':
      return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
    case 'shipped':
      return <TruckIcon className="h-5 w-5 text-blue-600" />;
    case 'cancelled':
      return <XCircleIcon className="h-5 w-5 text-red-600" />;
    default:
      return <ClockIcon className="h-5 w-5 text-yellow-600" />;
  }
};

export default function OrdersPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  // Redirect if not authenticated
  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const { data: ordersData, isLoading, error } = useQuery({
    queryKey: ['orders'],
    queryFn: async () => {
      const response = await api.get<OrdersResponse>('/orders/');
      return response.data;
    },
    enabled: isAuthenticated,
  });

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

  if (error) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-red-600">Failed to load orders. Please try again.</p>
        </div>
      </Layout>
    );
  }

  const orders = ordersData?.results || [];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Orders</h1>
          <p className="mt-2 text-gray-600">
            Track and manage your orders
          </p>
        </div>

        {orders.length === 0 ? (
          <div className="text-center py-12">
            <div className="bg-gray-100 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-4">
              <TruckIcon className="h-12 w-12 text-gray-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No orders yet</h2>
            <p className="text-gray-600 mb-8">Start shopping to see your orders here</p>
            <Link href="/products">
              <Button size="lg">Start Shopping</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                {/* Order Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(order.status)}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getOrderStatusColor(order.status)}`}>
                        {getOrderStatusText(order.status)}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        Order #{order.order_number}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Placed on {formatDate(order.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-medium text-gray-900">
                      {formatPrice(order.total_amount)}
                    </p>
                    <Link href={`/orders/${order.id}`}>
                      <Button variant="outline" size="sm">
                        <EyeIcon className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                    </Link>
                  </div>
                </div>

                {/* Order Items */}
                <div className="border-t border-gray-200 pt-4">
                  <div className="space-y-3">
                    {order.items.slice(0, 3).map((item) => (
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
                          {item.variant && (
                            <p className="text-sm text-gray-500">{item.variant.name}</p>
                          )}
                          <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                        </div>
                        <p className="text-sm font-medium text-gray-900">
                          {formatPrice(item.price * item.quantity)}
                        </p>
                      </div>
                    ))}
                    {order.items.length > 3 && (
                      <p className="text-sm text-gray-500 text-center">
                        +{order.items.length - 3} more item{order.items.length - 3 !== 1 ? 's' : ''}
                      </p>
                    )}
                  </div>
                </div>

                {/* Order Actions */}
                <div className="border-t border-gray-200 pt-4 mt-4">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      {order.items.length} item{order.items.length !== 1 ? 's' : ''} • 
                      Total: {formatPrice(order.total_amount)}
                    </div>
                    <div className="flex space-x-3">
                      {order.status === 'delivered' && (
                        <Button variant="outline" size="sm">
                          Reorder
                        </Button>
                      )}
                      {order.status === 'pending' && (
                        <Button variant="outline" size="sm">
                          Cancel Order
                        </Button>
                      )}
                      <Link href={`/orders/${order.id}`}>
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
