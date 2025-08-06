from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
import uuid
from .serializers import PaymentSerializer, CartTotalSerializer
from carts.models import Cart, CartItem
from products.models.product_models import Products
from orders.models import Order

User = get_user_model()


class PaymentSerializerTest(TestCase):
    def setUp(self):
        """Set up test data"""
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
        # Cart total: 10.99 * 2 = 21.98

    def test_serializer_fields(self):
        """Test that serializer has correct fields"""
        serializer = PaymentSerializer()
        expected_fields = {'cart_id', 'amount', 'status', 'created_at'}
        self.assertEqual(set(serializer.fields.keys()), expected_fields)

    def test_create_payment_success(self):
        """Test creating a payment successfully"""
        data = {
            'cart_id': str(self.cart.cart_id),
            'amount': '21.98',
            'status': 'paid'
        }
        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        
        self.assertEqual(payment.cart, self.cart)
        self.assertEqual(float(payment.amount), 21.98)
        self.assertIsNotNone(payment.created_at)

    def test_payment_amount_validation_fails(self):
        """Test payment fails when amount doesn't match cart total"""
        data = {
            'cart_id': str(self.cart.cart_id),
            'amount': '15.00',  # Wrong amount
            'status': 'paid'
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Amount does not match cart total', str(serializer.errors))

    def test_payment_with_invalid_cart(self):
        """Test payment fails with invalid cart ID"""
        data = {
            'cart_id': str(uuid.uuid4()),  # Non-existent cart
            'amount': '21.98',
            'status': 'paid'
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Cart not found', str(serializer.errors))

    def test_payment_updates_order_status(self):
        """Test payment updates order status when order exists"""
        # Create order for the cart
        order = Order.objects.create(cart=self.cart, payment_status='pending')
        
        data = {
            'cart_id': str(self.cart.cart_id),
            'amount': '21.98',
            'status': 'paid'
        }
        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        
        # Verify order status was updated
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(payment.cart, self.cart)


class CartTotalSerializerTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Products.objects.create(
            product_id=uuid.uuid4(),
            name='Test Product',
            description='Test Description',
            price=15.50,
            quantity=100,
            created_by=self.user
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )

    def test_cart_total_serializer_output(self):
        """Test cart total serializer output"""
        data = {
            'cart_id': str(self.cart.cart_id),
            'total_amount': '46.50'  # 15.50 * 3
        }
        serializer = CartTotalSerializer(data)
        serialized_data = serializer.data
        
        expected_fields = {'cart_id', 'total_amount'}
        self.assertEqual(set(serialized_data.keys()), expected_fields)
        self.assertEqual(serialized_data['cart_id'], str(self.cart.cart_id))
        self.assertEqual(float(serialized_data['total_amount']), 46.50)
