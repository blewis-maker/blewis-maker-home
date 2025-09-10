"""
Cart models for the e-commerce platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Cart(models.Model):
    """
    Shopping cart model.
    """
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='cart',
        null=True,
        blank=True
    )
    session_key = models.CharField(_('session key'), max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        db_table = 'carts'

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Cart {self.id}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def add_item(self, product, quantity=1, variant=None):
        """
        Add an item to the cart.
        """
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def remove_item(self, product, variant=None):
        """
        Remove an item from the cart.
        """
        try:
            cart_item = CartItem.objects.get(
                cart=self,
                product=product,
                variant=variant
            )
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def clear(self):
        """
        Clear all items from the cart.
        """
        self.items.all().delete()

    def get_or_create_cart(user=None, session_key=None):
        """
        Get or create a cart for a user or session.
        """
        if user:
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart


class CartItem(models.Model):
    """
    Cart item model.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        db_table = 'cart_items'
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        variant_text = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_text} x {self.quantity}"

    @property
    def unit_price(self):
        """
        Get the unit price for this item.
        """
        if self.variant:
            return self.variant.price
        return self.product.price

    @property
    def total_price(self):
        """
        Calculate the total price for this item.
        """
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        """
        Override save to validate stock availability.
        """
        if self.variant:
            if self.quantity > self.variant.stock_quantity:
                raise ValueError("Not enough stock for this variant")
        else:
            if self.quantity > self.product.stock_quantity:
                raise ValueError("Not enough stock for this product")
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """
    User wishlist model.
    """
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        db_table = 'wishlist_items'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"