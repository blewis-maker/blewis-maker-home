"""
Cart serializers for the e-commerce platform.
"""

from rest_framework import serializers
from .models import Cart, CartItem, Wishlist
from products.serializers import ProductListSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items.
    """
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    unit_price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'quantity', 'unit_price', 'total_price', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """
        Validate cart item data.
        """
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = data.get('quantity', 1)

        # Import here to avoid circular imports
        from products.models import Product, ProductVariant

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")

        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                    is_active=True
                )
                if quantity > variant.stock_quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock. Available: {variant.stock_quantity}"
                    )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found or inactive")
        else:
            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Not enough stock. Available: {product.stock_quantity}"
                )

        return data


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping cart.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'items', 'total_items',
            'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for wishlist items.
    """
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_product_id(self, value):
        """
        Validate that the product exists and is active.
        """
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")
        return value

    def validate(self, data):
        """
        Validate wishlist item data.
        """
        user = self.context['request'].user
        product_id = data.get('product_id')

        if Wishlist.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError("Product already in wishlist")

        return data


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding items to cart.
    """
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        """
        Validate add to cart data.
        """
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = data.get('quantity', 1)

        from products.models import Product, ProductVariant

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")

        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                    is_active=True
                )
                if quantity > variant.stock_quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock. Available: {variant.stock_quantity}"
                    )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found or inactive")

        return data


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantities.
    """
    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        """
        Validate quantity against stock availability.
        """
        cart_item = self.context.get('cart_item')
        if cart_item:
            if cart_item.variant:
                if value > cart_item.variant.stock_quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock. Available: {cart_item.variant.stock_quantity}"
                    )
            else:
                if value > cart_item.product.stock_quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock. Available: {cart_item.product.stock_quantity}"
                    )
        return value
