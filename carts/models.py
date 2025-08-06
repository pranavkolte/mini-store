import uuid

from django.db import models
from django.contrib.auth import get_user_model

from products.models.product_models import Products

User = get_user_model()


class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart'
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_item'
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
    