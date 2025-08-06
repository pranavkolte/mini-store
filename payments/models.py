from django.db import models
from carts.models import Cart
import uuid

class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment {self.payment_id} for cart {self.cart.cart_id}"