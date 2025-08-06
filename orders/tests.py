from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework import serializers
import uuid
from .serializers import OrderSerializer
from .models import Order
from carts.models import Cart, CartItem
from products.models.product_models import Products

User = get_user_model()


class OrderSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Products.objects.create(
            product_id=uuid.uuid4(),
            name='Test Product',
            description='Test Description',
            price=10.99,
            quantity=100,
            created_by=self.user
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

    def get_request_context(self):
        request = self.factory.post('/')
        request.user = self.user
        return {'request': Request(request)}

    def test_create_order_success(self):
        data = {
            'input_cart_id': str(self.cart.cart_id)
        }
        serializer = OrderSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        
        self.assertEqual(order.cart, self.cart)
        self.assertEqual(order.payment_status, 'pending')
        self.assertIsNotNone(order.checkout_time)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 98)

    def test_create_order_insufficient_stock(self):
        self.product.quantity = 1
        self.product.save()
        
        data = {
            'input_cart_id': str(self.cart.cart_id)
        }
        serializer = OrderSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.save()
        
        self.assertIn('detail', context.exception.detail)
        self.assertIn('Not enough stock', str(context.exception.detail['detail'][0]))

    def test_serializer_fields(self):
        serializer = OrderSerializer()
        expected_fields = {'cart_id', 'input_cart_id', 'payment_status', 'checkout_time'}
        self.assertEqual(set(serializer.fields.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = OrderSerializer()
        read_only_fields = {'cart_id', 'payment_status', 'checkout_time'}
        for field_name in read_only_fields:
            self.assertTrue(serializer.fields[field_name].read_only)

    def test_serialization_output(self):
        order = Order.objects.create(cart=self.cart, payment_status='pending')
        
        serializer = OrderSerializer(order)
        data = serializer.data
        
        expected_fields = {'cart_id', 'payment_status', 'checkout_time'}
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertEqual(data['cart_id'], str(self.cart.cart_id))
        self.assertEqual(data['payment_status'], 'pending')
        self.assertIsNotNone(data['checkout_time'])
        self.assertNotIn('input_cart_id', data)
