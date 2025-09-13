"""
Views for the products app.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import Brand, Category, Product, ProductImage, ProductVariant, ProductReview
from .serializers import (
    BrandSerializer, CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductImageSerializer, ProductVariantSerializer, ProductReviewSerializer,
    ProductSearchSerializer
)


class BrandListView(generics.ListCreateAPIView):
    """
    List and create brands.
    """
    queryset = Brand.objects.filter(is_active=True).order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific brand.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class CategoryListView(generics.ListCreateAPIView):
    """
    List and create categories.
    """
    queryset = Category.objects.filter(is_active=True, parent=None).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class ProductListView(generics.ListCreateAPIView):
    """
    List and create products.
    """
    queryset = Product.objects.filter(is_active=True).select_related(
        'brand', 'category'
    ).prefetch_related('images', 'variants', 'reviews')
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'category', 'is_featured']
    search_fields = ['name', 'description', 'short_description', 'brand__name']
    ordering_fields = ['name', 'price', 'created_at', 'average_rating']
    ordering = ['-created_at']


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific product.
    """
    queryset = Product.objects.filter(is_active=True).select_related(
        'brand', 'category'
    ).prefetch_related('images', 'variants', 'reviews')
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class ProductSearchView(APIView):
    """
    Advanced product search with filtering and pagination.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Search products with advanced filtering.
        """
        serializer = ProductSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        queryset = Product.objects.filter(is_active=True).select_related(
            'brand', 'category'
        ).prefetch_related('images', 'variants', 'reviews')
        
        # Apply filters
        if data.get('query'):
            queryset = queryset.filter(
                Q(name__icontains=data['query']) |
                Q(description__icontains=data['query']) |
                Q(short_description__icontains=data['query']) |
                Q(brand__name__icontains=data['query'])
            )
        
        if data.get('category'):
            queryset = queryset.filter(category__slug=data['category'])
        
        if data.get('brand'):
            queryset = queryset.filter(brand__slug=data['brand'])
        
        if data.get('min_price') is not None:
            queryset = queryset.filter(price__gte=data['min_price'])
        
        if data.get('max_price') is not None:
            queryset = queryset.filter(price__lte=data['max_price'])
        
        if data.get('min_rating') is not None:
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            ).filter(avg_rating__gte=data['min_rating'])
        
        if data.get('in_stock'):
            queryset = queryset.filter(
                variants__stock_quantity__gt=0,
                variants__is_active=True
            ).distinct()
        
        if data.get('is_featured'):
            queryset = queryset.filter(is_featured=True)
        
        # Apply ordering
        ordering = data.get('sort_by', '-created_at')
        if ordering == 'average_rating':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            ).order_by('-avg_rating')
        else:
            queryset = queryset.order_by(ordering)
        
        # Pagination
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize results
        serializer = ProductListSerializer(page_obj, many=True)
        
        return Response({
            'results': serializer.data,
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        })


class ProductImageView(generics.ListCreateAPIView):
    """
    List and create product images.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductImage.objects.filter(product_id=product_id).order_by('sort_order')

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product)


class ProductVariantView(generics.ListCreateAPIView):
    """
    List and create product variants.
    """
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductVariant.objects.filter(product_id=product_id, is_active=True)

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product)


class ProductReviewView(generics.ListCreateAPIView):
    """
    List and create product reviews.
    """
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(
            product_id=product_id, is_approved=True
        ).order_by('-created_at')

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product, user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_products_view(request):
    """
    Get featured products.
    """
    products = Product.objects.filter(
        is_active=True, is_featured=True
    ).select_related('brand', 'category').prefetch_related('images')[:8]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def new_products_view(request):
    """
    Get newest products.
    """
    products = Product.objects.filter(
        is_active=True
    ).select_related('brand', 'category').prefetch_related('images').order_by('-created_at')[:8]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def best_selling_products_view(request):
    """
    Get best selling products (based on order items).
    """
    from orders.models import OrderItem
    
    # Get products ordered by total quantity sold
    products = Product.objects.filter(
        is_active=True,
        order_items__order__status__in=['completed', 'shipped', 'delivered']
    ).annotate(
        total_sold=Count('order_items')
    ).order_by('-total_sold')[:8]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_stats_view(request):
    """
    Get product statistics.
    """
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_brands = Brand.objects.filter(is_active=True).count()
    featured_products = Product.objects.filter(is_active=True, is_featured=True).count()
    
    return Response({
        'total_products': total_products,
        'total_categories': total_categories,
        'total_brands': total_brands,
        'featured_products': featured_products,
    })