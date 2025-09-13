'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useCart } from '@/contexts/CartContext';
import { 
  ShoppingCartIcon, 
  UserIcon, 
  MagnifyingGlassIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import Button from './ui/Button';

const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { cart } = useCart();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const cartItemCount = cart?.total_items || 0;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="text-2xl font-bold text-blue-600">
              E-Commerce Demo
            </Link>
          </div>

          {/* Search Bar - Desktop */}
          <div className="hidden md:flex flex-1 max-w-lg mx-8">
            <div className="relative w-full">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>

          {/* Navigation - Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/products"
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Products
            </Link>
            <Link
              href="/orders"
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Orders
            </Link>
            
            {/* Cart */}
            <Link
              href="/cart"
              className="relative p-2 text-gray-700 hover:text-blue-600 transition-colors"
            >
              <ShoppingCartIcon className="h-6 w-6" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {cartItemCount}
                </span>
              )}
            </Link>

            {/* User Menu */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <Link
                  href="/account"
                  className="flex items-center text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  <UserIcon className="h-5 w-5 mr-2" />
                  {user?.first_name}
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={logout}
                >
                  Logout
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">
                    Sign Up
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100 transition-colors"
            >
              {isMobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Search */}
        <div className="md:hidden pb-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>

        {/* Mobile menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            <div className="space-y-2">
              <Link
                href="/products"
                className="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md text-base font-medium transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Products
              </Link>
              <Link
                href="/categories"
                className="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md text-base font-medium transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Categories
              </Link>
              <Link
                href="/cart"
                className="flex items-center px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md text-base font-medium transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <ShoppingCartIcon className="h-5 w-5 mr-2" />
                Cart
                {cartItemCount > 0 && (
                  <span className="ml-2 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {cartItemCount}
                  </span>
                )}
              </Link>
              
              {isAuthenticated ? (
                <div className="space-y-2 pt-2 border-t border-gray-200">
                  <Link
                    href="/account"
                    className="flex items-center px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md text-base font-medium transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <UserIcon className="h-5 w-5 mr-2" />
                    {user?.first_name}
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md text-base font-medium transition-colors"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="space-y-2 pt-2 border-t border-gray-200">
                  <Link
                    href="/login"
                    className="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md text-base font-medium transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    href="/register"
                    className="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md text-base font-medium transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
