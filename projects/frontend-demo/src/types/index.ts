// User Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
}

export interface UserProfile {
  id: number;
  user: number;
  phone?: string;
  date_of_birth?: string;
  avatar?: string;
  bio?: string;
  created_at: string;
  updated_at: string;
}

export interface Address {
  id: number;
  user: number;
  type: 'billing' | 'shipping';
  first_name: string;
  last_name: string;
  company?: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// Product Types
export interface Brand {
  id: number;
  name: string;
  slug: string;
  description?: string;
  logo?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image?: string;
  is_active: boolean;
  parent?: number;
  children?: Category[];
  created_at: string;
  updated_at: string;
}

export interface ProductImage {
  id: number;
  product: number;
  image: string;
  alt_text?: string;
  is_primary: boolean;
  sort_order: number;
  created_at: string;
}

export interface ProductVariant {
  id: number;
  product: number;
  name: string;
  sku: string;
  price: number;
  compare_price?: number;
  cost_price?: number;
  stock_quantity: number;
  is_active: boolean;
  attributes: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  short_description?: string;
  sku: string;
  brand: Brand;
  category: Category;
  images: ProductImage[];
  variants: ProductVariant[];
  primary_image?: ProductImage;
  average_rating: number;
  review_count: number;
  has_variants: boolean;
  min_price: number;
  max_price: number;
  is_in_stock: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Cart Types
export interface CartItem {
  id: number;
  cart: number;
  product: Product;
  variant?: ProductVariant;
  quantity: number;
  price: number;
  created_at: string;
  updated_at: string;
}

export interface Cart {
  id: number;
  user: number;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  created_at: string;
  updated_at: string;
}

export interface WishlistItem {
  id: number;
  user: number;
  product: Product;
  created_at: string;
}

// Order Types
export interface OrderItem {
  id: number;
  order: number;
  product: Product;
  variant?: ProductVariant;
  quantity: number;
  price: number;
  total: number;
  created_at: string;
}

export interface Order {
  id: number;
  user: number;
  order_number: string;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';
  billing_address: Address;
  shipping_address: Address;
  items: OrderItem[];
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  discount_amount: number;
  total_amount: number;
  coupon?: Coupon;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Coupon {
  id: number;
  code: string;
  description: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  minimum_amount?: number;
  maximum_discount?: number;
  usage_limit?: number;
  used_count: number;
  is_active: boolean;
  valid_from: string;
  valid_until: string;
  created_at: string;
  updated_at: string;
}

// Payment Types
export interface Payment {
  id: number;
  order: number;
  stripe_payment_intent_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed' | 'cancelled';
  payment_method: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentMethod {
  id: number;
  user: number;
  stripe_payment_method_id: string;
  type: string;
  card_last4?: string;
  card_brand?: string;
  card_exp_month?: number;
  card_exp_year?: number;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export interface AddressForm {
  type: 'billing' | 'shipping';
  first_name: string;
  last_name: string;
  company?: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string;
  is_default: boolean;
}

export interface CheckoutForm {
  billing_address: AddressForm;
  shipping_address: AddressForm;
  coupon_code?: string;
  notes?: string;
}
