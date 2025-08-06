from rest_framework import serializers
from .models import Cart, CartItem
from products.models.product_models import Products


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    cart_id = serializers.UUIDField(source='cart.cart_id', read_only=True)  # <-- add this line

    class Meta:
        model = CartItem
        fields = ['id', 'cart_id', 'product_id', 'quantity', 'added_at']
        read_only_fields = ['id', 'added_at', 'cart_id']

    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data.pop('product_id')
        cart_id = validated_data.pop('cart_id', None)
        product = Products.objects.get(product_id=product_id)
        if cart_id:
            cart = Cart.objects.get(cart_id=cart_id, user=user)
        else:
            cart, _ = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': validated_data.get('quantity', 1)}
        )
        if not created:
            cart_item.quantity += validated_data.get('quantity', 1)
            cart_item.save()
        return cart_item
    