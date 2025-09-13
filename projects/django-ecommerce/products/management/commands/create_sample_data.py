"""
Django management command to create sample product data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Brand, Category, Product, ProductImage, ProductVariant, ProductReview
from accounts.models import User
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample product data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            ProductReview.objects.all().delete()
            ProductVariant.objects.all().delete()
            ProductImage.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()

        self.stdout.write('Creating sample data...')
        
        with transaction.atomic():
            # Create brands
            brands = self.create_brands()
            
            # Create categories
            categories = self.create_categories()
            
            # Create products
            products = self.create_products(brands, categories)
            
            # Create product variants
            self.create_product_variants(products)
            
            # Create product reviews
            self.create_product_reviews(products)

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_brands(self):
        """Create sample brands."""
        brands_data = [
            {'name': 'TechCorp', 'description': 'Leading technology company'},
            {'name': 'FashionHub', 'description': 'Trendy fashion brand'},
            {'name': 'HomeStyle', 'description': 'Home and lifestyle products'},
            {'name': 'SportsMax', 'description': 'Sports and fitness equipment'},
            {'name': 'BeautyPlus', 'description': 'Beauty and cosmetics'},
        ]
        
        brands = []
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults=brand_data
            )
            brands.append(brand)
            if created:
                self.stdout.write(f'Created brand: {brand.name}')
        
        return brands

    def create_categories(self):
        """Create sample categories."""
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden'},
            {'name': 'Sports', 'description': 'Sports and fitness equipment'},
            {'name': 'Beauty', 'description': 'Beauty and personal care'},
            {'name': 'Books', 'description': 'Books and educational materials'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories

    def create_products(self, brands, categories):
        """Create sample products."""
        products_data = [
            {
                'name': 'Smartphone Pro Max',
                'description': 'Latest smartphone with advanced features',
                'short_description': 'High-end smartphone',
                'brand': brands[0],  # TechCorp
                'category': categories[0],  # Electronics
                'price': Decimal('999.99'),
                'compare_price': Decimal('1199.99'),
                'sku': 'SPM-001',
                'stock_quantity': random.randint(10, 100),
                'is_featured': True,
            },
            {
                'name': 'Wireless Headphones',
                'description': 'Premium wireless headphones with noise cancellation',
                'short_description': 'Noise-cancelling headphones',
                'brand': brands[0],  # TechCorp
                'category': categories[0],  # Electronics
                'price': Decimal('299.99'),
                'compare_price': Decimal('399.99'),
                'sku': 'WH-001',
                'stock_quantity': random.randint(10, 100),
                'is_featured': True,
            },
            {
                'name': 'Designer T-Shirt',
                'description': 'Comfortable cotton t-shirt with modern design',
                'short_description': 'Premium cotton t-shirt',
                'brand': brands[1],  # FashionHub
                'category': categories[1],  # Clothing
                'price': Decimal('49.99'),
                'compare_price': Decimal('69.99'),
                'sku': 'DT-001',
                'stock_quantity': random.randint(10, 100),
                'is_featured': False,
            },
            {
                'name': 'Running Shoes',
                'description': 'High-performance running shoes for athletes',
                'short_description': 'Professional running shoes',
                'brand': brands[3],  # SportsMax
                'category': categories[3],  # Sports
                'price': Decimal('129.99'),
                'compare_price': Decimal('159.99'),
                'sku': 'RS-001',
                'stock_quantity': random.randint(10, 100),
                'is_featured': True,
            },
            {
                'name': 'Coffee Maker',
                'description': 'Automatic coffee maker with programmable features',
                'short_description': 'Programmable coffee maker',
                'brand': brands[2],  # HomeStyle
                'category': categories[2],  # Home & Garden
                'price': Decimal('199.99'),
                'compare_price': Decimal('249.99'),
                'sku': 'CM-001',
                'stock_quantity': random.randint(10, 100),
                'is_featured': False,
            },
            {
                'name': 'Skincare Set',
                'description': 'Complete skincare routine set',
                'short_description': 'Premium skincare collection',
                'brand': brands[4],  # BeautyPlus
                'category': categories[4],  # Beauty
                'price': Decimal('89.99'),
                'compare_price': Decimal('119.99'),
                'sku': 'SS-001',
                'stock_quantity': random.randint(10, 100),
                'is_featured': True,
            },
        ]
        
        products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        return products

    def create_product_variants(self, products):
        """Create product variants."""
        for product in products:
            # Create 2-3 variants per product
            num_variants = random.randint(2, 3)
            colors = ['Black', 'White', 'Blue', 'Red', 'Green']
            sizes = ['S', 'M', 'L', 'XL', 'XXL']
            
            for i in range(num_variants):
                color = random.choice(colors)
                size = random.choice(sizes) if product.category.name == 'Clothing' else None
                
                variant_name = f"{color}"
                if size:
                    variant_name += f" - {size}"
                
                price_variation = random.uniform(0.8, 1.2)
                variant_price = product.price * Decimal(str(price_variation))
                
                ProductVariant.objects.get_or_create(
                    product=product,
                    name=variant_name,
                    defaults={
                        'sku': f"{product.sku}-{i+1}",
                        'price': variant_price,
                        'stock_quantity': random.randint(10, 100),
                        'is_active': True,
                    }
                )

    def create_product_reviews(self, products):
        """Create product reviews."""
        # Create multiple test users for reviews
        users = []
        for i in range(10):  # Create 10 different users
            user, created = User.objects.get_or_create(
                email=f'reviewer{i+1}@example.com',
                defaults={
                    'username': f'reviewer{i+1}',
                    'first_name': f'Reviewer{i+1}',
                    'last_name': 'User',
                }
            )
            users.append(user)
        
        review_templates = [
            {'rating': 5, 'title': 'Excellent product!', 'comment': 'Highly recommended, great quality.'},
            {'rating': 4, 'title': 'Very good', 'comment': 'Good product, meets expectations.'},
            {'rating': 3, 'title': 'Average', 'comment': 'Decent product, nothing special.'},
            {'rating': 2, 'title': 'Disappointed', 'comment': 'Not as expected, quality issues.'},
            {'rating': 1, 'title': 'Poor quality', 'comment': 'Very disappointed, would not recommend.'},
        ]
        
        for product in products:
            # Create 3-5 reviews per product
            num_reviews = random.randint(3, 5)
            for i in range(num_reviews):
                review_data = random.choice(review_templates)
                user = random.choice(users)  # Use different users
                ProductReview.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={
                        'rating': review_data['rating'],
                        'title': review_data['title'],
                        'comment': review_data['comment'],
                        'is_approved': True,
                        'is_verified_purchase': random.choice([True, False]),
                    }
                )
