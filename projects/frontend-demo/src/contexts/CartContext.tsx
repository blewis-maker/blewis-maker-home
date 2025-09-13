'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Cart, CartItem, Product, ProductVariant } from '@/types';
import { useAuth } from './AuthContext';
import api from '@/lib/api';

interface CartContextType {
  cart: Cart | null;
  isLoading: boolean;
  addToCart: (productId: number, variantId?: number, quantity?: number) => Promise<void>;
  removeFromCart: (itemId: number) => Promise<void>;
  updateQuantity: (itemId: number, quantity: number) => Promise<void>;
  clearCart: () => Promise<void>;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: React.ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  // Load cart when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshCart();
    } else {
      setCart(null);
    }
  }, [isAuthenticated]);

  const refreshCart = async () => {
    if (!isAuthenticated) return;
    
    try {
      setIsLoading(true);
      const response = await api.get('/cart/');
      setCart(response.data);
    } catch (error) {
      console.error('Failed to load cart:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = async (productId: number, variantId?: number, quantity: number = 1) => {
    if (!isAuthenticated) {
      throw new Error('Please log in to add items to cart');
    }

    try {
      const response = await api.post('/cart/add/', {
        product_id: productId,
        variant_id: variantId,
        quantity,
      });
      
      // Refresh cart to get updated data
      await refreshCart();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to add item to cart');
    }
  };

  const removeFromCart = async (itemId: number) => {
    if (!isAuthenticated) return;

    try {
      await api.delete(`/cart/items/${itemId}/`);
      await refreshCart();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to remove item from cart');
    }
  };

  const updateQuantity = async (itemId: number, quantity: number) => {
    if (!isAuthenticated) return;

    if (quantity <= 0) {
      await removeFromCart(itemId);
      return;
    }

    try {
      await api.patch(`/cart/items/${itemId}/`, { quantity });
      await refreshCart();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to update quantity');
    }
  };

  const clearCart = async () => {
    if (!isAuthenticated) return;

    try {
      await api.delete('/cart/clear/');
      await refreshCart();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to clear cart');
    }
  };

  const value: CartContextType = {
    cart,
    isLoading,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    refreshCart,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};
