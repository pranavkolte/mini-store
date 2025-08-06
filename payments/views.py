from rest_framework import generics, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from carts.models import Cart
from .serializers import PaymentSerializer, CartTotalSerializer

class CreatePaymentView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a payment for a cart",
        request_body=PaymentSerializer,
        responses={201: PaymentSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CartTotalView(generics.GenericAPIView):
    serializer_class = CartTotalSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the total amount for a cart",
        manual_parameters=[
            openapi.Parameter(
                'cart_id', openapi.IN_QUERY, description="Cart UUID", type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={200: CartTotalSerializer}
    )
    def get(self, request, *args, **kwargs):
        cart_id = request.query_params.get('cart_id')
        try:
            cart = Cart.objects.get(cart_id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({'detail': 'Cart not found.'}, status=404)
        total = sum(item.product.price * item.quantity for item in cart.items.all())
        return Response({'cart_id': cart_id, 'total_amount': total})
