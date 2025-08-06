from django.db import models
from carts.models import Cart

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='order', primary_key=True)
    payment_status = models.CharField(max_length=32, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed')
    ], default='pending')
    checkout_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order for cart {self.cart.cart_id} - {self.payment_status}"
    
    def get_total_price(self):
        total = sum(item.product.price * item.quantity for item in self.cart.items.all())
        return total