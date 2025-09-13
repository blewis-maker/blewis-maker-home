"""
Cart views for the e-commerce platform.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from .models import Cart, CartItem, Wishlist
from .serializers import (
    CartSerializer, CartItemSerializer, WishlistSerializer,
    AddToCartSerializer, UpdateCartItemSerializer
)
from products.models import Product, ProductVariant


class CartView(generics.RetrieveAPIView):
    """
    Retrieve the current user's cart.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Get or create cart for the current user.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemListView(generics.ListCreateAPIView):
    """
    List and create cart items.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get cart items for the current user.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def perform_create(self, serializer):
        """
        Create a new cart item.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a cart item.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get cart items for the current user.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    """
    Add an item to the cart.
    """
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )

        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                    is_active=True
                )
            except ProductVariant.DoesNotExist:
                return Response(
                    {'error': 'Product variant not found or inactive'},
                    status=status.HTTP_404_NOT_FOUND
                )

        cart, created = Cart.objects.get_or_create(user=request.user)
        
        try:
            cart_item = cart.add_item(product, quantity, variant)
            cart_item_serializer = CartItemSerializer(cart_item)
            return Response(cart_item_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, product_id):
    """
    Remove an item from the cart.
    """
    variant_id = request.data.get('variant_id')
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found or inactive'},
            status=status.HTTP_404_NOT_FOUND
        )

    variant = None
    if variant_id:
        try:
            variant = ProductVariant.objects.get(
                id=variant_id,
                product=product,
                is_active=True
            )
        except ProductVariant.DoesNotExist:
            return Response(
                {'error': 'Product variant not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )

    cart, created = Cart.objects.get_or_create(user=request.user)
    success = cart.remove_item(product, variant)
    
    if success:
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Item not found in cart'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Update cart item quantity.
    """
    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__user=request.user
        )
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UpdateCartItemSerializer(
        data=request.data,
        context={'cart_item': cart_item}
    )
    
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']
        try:
            cart_item.quantity = quantity
            cart_item.save()
            cart_item_serializer = CartItemSerializer(cart_item)
            return Response(cart_item_serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    """
    Clear all items from the cart.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.clear()
    return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)


class WishlistView(generics.ListCreateAPIView):
    """
    List and create wishlist items.
    """
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get wishlist items for the current user.
        """
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new wishlist item.
        """
        serializer.save(user=self.request.user)


class WishlistDetailView(generics.DestroyAPIView):
    """
    Delete a wishlist item.
    """
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get wishlist items for the current user.
        """
        return Wishlist.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_wishlist(request):
    """
    Add an item to the wishlist.
    """
    product_id = request.data.get('product_id')
    
    if not product_id:
        return Response(
            {'error': 'product_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found or inactive'},
            status=status.HTTP_404_NOT_FOUND
        )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(
            {'error': 'Product already in wishlist'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_wishlist(request, product_id):
    """
    Remove an item from the wishlist.
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found or inactive'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        wishlist_item = Wishlist.objects.get(
            user=request.user,
            product=product
        )
        wishlist_item.delete()
        return Response({'message': 'Item removed from wishlist'}, status=status.HTTP_200_OK)
    except Wishlist.DoesNotExist:
        return Response(
            {'error': 'Item not found in wishlist'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cart_summary(request):
    """
    Get cart summary information.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    summary = {
        'total_items': cart.total_items,
        'total_price': float(cart.total_price),
        'item_count': cart.items.count()
    }
    
    return Response(summary, status=status.HTTP_200_OK)