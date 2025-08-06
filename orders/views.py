from django.db import IntegrityError
from rest_framework import generics, permissions, serializers
from carts.models import Cart
from .models import Order
from .serializers import OrderSerializer


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        user = self.request.user
        cart = Cart.objects.filter(user=user).order_by('-created_at').first()
        if not cart or not cart.items.exists():
            raise serializers.ValidationError({'detail': 'Cart is empty.'})
        if hasattr(cart, 'order'):
            raise serializers.ValidationError({'detail': 'Order already exists for this cart.'})
        try:
            serializer.save(cart_id=cart.cart_id)
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'Order already exists for this cart.'})

class ListOrderView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(cart__user=user)
    
class DeleteOrderView(generics.DestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(cart__user=user)
    