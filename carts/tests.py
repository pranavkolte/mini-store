from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.request import Request
import uuid
from .serializers import CartItemSerializer
from .models import Cart, CartItem
from products.models.product_models import Products

User = get_user_model()


class CartItemSerializerTest(TestCase):
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

    def get_request_context(self):
        """Helper method to create request context"""
        request = self.factory.post('/')
        force_authenticate(request, user=self.user) 
        return {'request': Request(request)}

    def test_serializer_fields(self):
        """Test that serializer has correct fields"""
        serializer = CartItemSerializer()
        expected_fields = {'id', 'cart_id', 'product_id', 'quantity', 'added_at'}
        self.assertEqual(set(serializer.fields.keys()), expected_fields)

    def test_read_only_fields(self):
        """Test that specified fields are read-only"""
        serializer = CartItemSerializer()
        read_only_fields = {'id', 'added_at', 'cart_id'}
        for field_name in read_only_fields:
            self.assertTrue(serializer.fields[field_name].read_only)

    def test_write_only_fields(self):
        """Test that product_id is write-only"""
        serializer = CartItemSerializer()
        self.assertTrue(serializer.fields['product_id'].write_only)

    def test_create_new_cart_item(self):
        """Test creating a new cart item"""
        data = {
            'product_id': str(self.product.product_id),
            'quantity': 2
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()
        
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.cart.user, self.user)

    def test_create_cart_item_with_existing_cart(self):
        """Test creating cart item with specific cart_id"""
        data = {
            'product_id': str(self.product.product_id),
            'cart_id': str(self.cart.cart_id),
            'quantity': 3
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()
        
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.quantity, 3)

    def test_update_existing_cart_item_quantity(self):
        """Test that adding existing product increases quantity"""
        existing_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        data = {
            'product_id': str(self.product.product_id),
            'quantity': 2
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()
        
        existing_item.refresh_from_db()
        self.assertEqual(existing_item.quantity, 3)
        self.assertEqual(cart_item.id, existing_item.id)

    def test_create_cart_item_default_quantity(self):
        """Test creating cart item with default quantity"""
        data = {
            'product_id': str(self.product.product_id)
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()
        
        self.assertEqual(cart_item.quantity, 1)

    def test_create_cart_when_none_exists(self):
        """Test that cart is created when user has no cart"""
        self.cart.delete()
        
        data = {
            'product_id': str(self.product.product_id),
            'quantity': 1
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()
        
        new_cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart_item.cart, new_cart)

    def test_invalid_product_id(self):
        """Test serializer with invalid product_id"""
        data = {
            'product_id': str(uuid.uuid4()),
            'quantity': 1
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(Products.DoesNotExist):
            serializer.save()

    def test_serialization_output(self):
        """Test serializer output contains correct fields"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        serializer = CartItemSerializer(cart_item)
        data = serializer.data
        
        expected_fields = {'id', 'cart_id', 'quantity', 'added_at'}
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertEqual(data['cart_id'], str(self.cart.cart_id))
        self.assertEqual(data['quantity'], 2)
        self.assertNotIn('product_id', data)

    def test_negative_quantity_validation(self):
        """Test that negative quantities are handled appropriately"""
        data = {
            'product_id': str(self.product.product_id),
            'quantity': -1
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)

    def test_zero_quantity_validation(self):
        """Test that zero quantities are handled appropriately"""
        data = {
            'product_id': str(self.product.product_id),
            'quantity': 0
        }
        serializer = CartItemSerializer(data=data, context=self.get_request_context())
        self.assertTrue(serializer.is_valid())