import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Product } from '../types';
import { formatPrice } from '../lib/utils';
import Button from './ui/Button';
import { useCart } from '../contexts/CartContext';
import { ShoppingCartIcon, HeartIcon } from '@heroicons/react/24/outline';

interface ProductCardProps {
  product: Product;
  onAddToWishlist?: (productId: number) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onAddToWishlist }) => {
  const { addToCart } = useCart();
  const [isAddingToCart, setIsAddingToCart] = React.useState(false);

  const handleAddToCart = async () => {
    try {
      setIsAddingToCart(true);
      await addToCart(product.id);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    } finally {
      setIsAddingToCart(false);
    }
  };

  const handleAddToWishlist = () => {
    if (onAddToWishlist) {
      onAddToWishlist(product.id);
    }
  };

  return (
    <div className="group relative bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden bg-gray-200">
        <Link href={`/products/${product.slug}`}>
          <Image
            src={product.primary_image?.image || '/placeholder-product.jpg'}
            alt={product.primary_image?.alt_text || product.name}
            width={300}
            height={300}
            className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
          />
        </Link>
      </div>
      
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-500">{product.brand.name}</span>
          <button
            onClick={handleAddToWishlist}
            className="text-gray-400 hover:text-red-500 transition-colors"
          >
            <HeartIcon className="h-5 w-5" />
          </button>
        </div>
        
        <Link href={`/products/${product.slug}`}>
          <h3 className="text-lg font-medium text-gray-900 hover:text-blue-600 transition-colors line-clamp-2">
            {product.name}
          </h3>
        </Link>
        
        <div className="mt-2 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg font-semibold text-gray-900">
              {formatPrice(product.min_price)}
            </span>
            {product.max_price > product.min_price && (
              <span className="text-sm text-gray-500">
                - {formatPrice(product.max_price)}
              </span>
            )}
          </div>
          
          {product.average_rating > 0 && (
            <div className="flex items-center">
              <div className="flex items-center">
                {[...Array(5)].map((_, i) => (
                  <svg
                    key={i}
                    className={`h-4 w-4 ${
                      i < Math.floor(product.average_rating)
                        ? 'text-yellow-400'
                        : 'text-gray-300'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <span className="ml-1 text-sm text-gray-500">
                ({product.review_count})
              </span>
            </div>
          )}
        </div>
        
        <div className="mt-4">
          <Button
            onClick={handleAddToCart}
            disabled={!product.is_in_stock || isAddingToCart}
            isLoading={isAddingToCart}
            className="w-full"
            size="sm"
          >
            <ShoppingCartIcon className="h-4 w-4 mr-2" />
            {product.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
