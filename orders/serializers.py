from rest_framework import serializers
from .models import Order
from carts.models import Cart

class OrderSerializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField(source='cart.cart_id', read_only=True)  # <-- read-only for response
    input_cart_id = serializers.UUIDField(write_only=True)  # <-- for input

    class Meta:
        model = Order
        fields = ['cart_id', 'input_cart_id', 'payment_status', 'checkout_time']
        read_only_fields = ['cart_id', 'payment_status', 'checkout_time']

    def create(self, validated_data):
        cart_id = validated_data.pop('input_cart_id')
        cart = Cart.objects.get(cart_id=cart_id)
        items = cart.items.select_related('product').all()
        errors = []
        # Check stock
        for item in items:
            if item.quantity > item.product.quantity:
                errors.append(f"Not enough stock for {item.product.name} (requested: {item.quantity}, available: {item.product.quantity})")
        if errors:
            raise serializers.ValidationError({'detail': errors})
        # Create order
        order = Order.objects.create(cart=cart, payment_status='pending')
        # Deduct stock
        for item in items:
            product = item.product
            product.quantity -= item.quantity
            product.save()
        return order
    