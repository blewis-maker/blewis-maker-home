"""
Management command to create sample coupons.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from orders.models import Coupon


class Command(BaseCommand):
    help = 'Create sample coupons for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing coupons before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing coupons...')
            Coupon.objects.all().delete()

        self.stdout.write('Creating sample coupons...')

        # Create sample coupons
        coupons_data = [
            {
                'code': 'WELCOME10',
                'description': 'Welcome discount - 10% off your first order',
                'coupon_type': 'percentage',
                'value': Decimal('10.00'),
                'minimum_amount': Decimal('50.00'),
                'maximum_discount': Decimal('25.00'),
                'usage_limit': 100,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30),
            },
            {
                'code': 'SAVE20',
                'description': 'Save $20 on orders over $100',
                'coupon_type': 'fixed',
                'value': Decimal('20.00'),
                'minimum_amount': Decimal('100.00'),
                'usage_limit': 50,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=60),
            },
            {
                'code': 'FREESHIP',
                'description': 'Free shipping on orders over $75',
                'coupon_type': 'fixed',
                'value': Decimal('15.00'),
                'minimum_amount': Decimal('75.00'),
                'maximum_discount': Decimal('15.00'),
                'usage_limit': 200,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=90),
            },
            {
                'code': 'HOLIDAY25',
                'description': 'Holiday special - 25% off',
                'coupon_type': 'percentage',
                'value': Decimal('25.00'),
                'minimum_amount': Decimal('200.00'),
                'maximum_discount': Decimal('100.00'),
                'usage_limit': 25,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=14),
            },
            {
                'code': 'STUDENT15',
                'description': 'Student discount - 15% off',
                'coupon_type': 'percentage',
                'value': Decimal('15.00'),
                'minimum_amount': Decimal('30.00'),
                'usage_limit': 500,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=365),
            },
        ]

        created_count = 0
        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created coupon: {coupon.code}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} coupons!')
        )
