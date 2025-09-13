"""
Serializers for the products app.
"""

from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (
    Brand, Category, Product, ProductImage, ProductVariant, ProductReview
)


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for Brand model.
    """
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = (
            'id', 'name', 'slug', 'description', 'logo', 'website',
            'is_active', 'created_at', 'updated_at', 'product_count'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    product_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'image', 'parent',
            'is_active', 'created_at', 'updated_at',
            'product_count', 'subcategories'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

    def get_subcategories(self, obj):
        subcategories = obj.children.filter(is_active=True).order_by('name')
        return CategorySerializer(subcategories, many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage model.
    """
    class Meta:
        model = ProductImage
        fields = (
            'id', 'image', 'alt_text', 'is_primary', 'sort_order',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductVariant model.
    """
    class Meta:
        model = ProductVariant
        fields = (
            'id', 'product', 'sku', 'name', 'price', 'compare_price',
            'cost_price', 'stock_quantity', 'is_active', 'attributes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductReview model.
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = (
            'id', 'product', 'user', 'user_name', 'user_avatar', 'rating',
            'title', 'comment', 'is_verified_purchase', 'is_approved',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_user_avatar(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            return obj.user.profile.avatar.url
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for Product list view (optimized for performance).
    """
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'brand', 'category', 'primary_image',
            'price', 'compare_price', 'average_rating', 'review_count',
            'price_range', 'in_stock', 'is_featured', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None

    def get_average_rating(self, obj):
        return obj.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()

    def get_price_range(self, obj):
        variants = obj.variants.filter(is_active=True)
        if variants.exists():
            prices = variants.values_list('price', flat=True)
            return {
                'min': min(prices),
                'max': max(prices)
            }
        return {'min': obj.price, 'max': obj.price}

    def get_in_stock(self, obj):
        return obj.variants.filter(is_active=True, stock_quantity__gt=0).exists()


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Product detail view (comprehensive data).
    """
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'short_description',
            'brand', 'category', 'images', 'variants', 'reviews',
            'price', 'compare_price', 'cost_price', 'sku', 'barcode',
            'weight', 'dimensions', 'average_rating', 'review_count',
            'related_products', 'is_featured', 'is_active', 'meta_title',
            'meta_description', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_average_rating(self, obj):
        return obj.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()

    def get_related_products(self, obj):
        related = Product.objects.filter(
            category=obj.category,
            is_active=True
        ).exclude(id=obj.id)[:4]
        return ProductListSerializer(related, many=True).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Product create/update operations.
    """
    images = ProductImageSerializer(many=True, required=False)
    variants = ProductVariantSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = (
            'name', 'description', 'short_description', 'brand', 'category',
            'price', 'compare_price', 'cost_price', 'sku', 'barcode',
            'weight', 'dimensions', 'is_featured', 'is_active',
            'meta_title', 'meta_description', 'images', 'variants'
        )

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        variants_data = validated_data.pop('variants', [])
        
        product = Product.objects.create(**validated_data)
        
        # Create images
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        # Create variants
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)
        
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        variants_data = validated_data.pop('variants', [])
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update images
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        
        # Update variants
        if variants_data:
            instance.variants.all().delete()
            for variant_data in variants_data:
                ProductVariant.objects.create(product=instance, **variant_data)
        
        return instance


class ProductSearchSerializer(serializers.Serializer):
    """
    Serializer for product search functionality.
    """
    query = serializers.CharField(max_length=255, required=False)
    category = serializers.CharField(max_length=255, required=False)
    brand = serializers.CharField(max_length=255, required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    min_rating = serializers.FloatField(min_value=0, max_value=5, required=False)
    in_stock = serializers.BooleanField(required=False)
    is_featured = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(
        choices=[
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('price', 'Price Low to High'),
            ('-price', 'Price High to Low'),
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-average_rating', 'Highest Rated'),
        ],
        required=False,
        default='-created_at'
    )
    page = serializers.IntegerField(min_value=1, required=False, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, required=False, default=20)
