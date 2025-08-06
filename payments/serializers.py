from rest_framework import serializers
from .models import Payment
from carts.models import Cart


class PaymentSerializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField(write_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField(max_length=32)

    class Meta:
        model = Payment
        fields = ['cart_id', 'amount', 'status', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, attrs):
        cart_id = attrs.get('cart_id')
        amount = attrs.get('amount')
        try:
            cart = Cart.objects.get(cart_id=cart_id)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart not found.")
        # Calculate total from cart
        total = sum(item.product.price * item.quantity for item in cart.items.all())
        if amount != total:
            raise serializers.ValidationError(f"Amount does not match cart total: {total}")
        attrs['cart'] = cart
        return attrs

    def create(self, validated_data):
        cart = validated_data['cart']
        amount = validated_data['amount']
        status = validated_data['status']
        payment = Payment.objects.create(cart=cart, amount=amount)
        payment.status = status
        payment.save()
        # Update order status if exists
        if hasattr(cart, 'order'):
            cart.order.payment_status = status
            cart.order.save()
        return payment


class CartTotalSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
