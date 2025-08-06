from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.request import Request
from rest_framework.exceptions import PermissionDenied
import uuid
from .serializers.product_serializers import ProductSerializer
from .models.product_models import Products
from .views.product_views import ProductUpdateView, ProductDeleteView

User = get_user_model()


class ProductSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
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

    def get_request_context(self):
        request = self.factory.post('/')
        force_authenticate(request, user=self.user)
        return {'request': Request(request)}

    def test_serializer_fields(self):
        serializer = ProductSerializer()
        expected_fields = {
            'product_id', 'name', 'description', 'quantity', 
            'price', 'created_by', 'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.fields.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = ProductSerializer()
        read_only_fields = {'product_id', 'created_by', 'created_at', 'updated_at'}
        for field_name in read_only_fields:
            self.assertTrue(serializer.fields[field_name].read_only)

    def test_create_product_success(self):
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 15.99,
            'quantity': 50
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        product = serializer.save(created_by=self.user)
        
        self.assertEqual(product.name, 'New Product')
        self.assertEqual(product.description, 'New Description')
        self.assertEqual(float(product.price), 15.99)
        self.assertEqual(product.quantity, 50)
        self.assertEqual(product.created_by, self.user)

    def test_update_product_success(self):
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 20.99,
            'quantity': 75
        }
        serializer = ProductSerializer(self.product, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_product = serializer.save()
        
        self.assertEqual(updated_product.name, 'Updated Product')
        self.assertEqual(updated_product.description, 'Updated Description')
        self.assertEqual(float(updated_product.price), 20.99)
        self.assertEqual(updated_product.quantity, 75)

    def test_serialization_output(self):
        serializer = ProductSerializer(self.product)
        data = serializer.data
        
        expected_fields = {
            'product_id', 'name', 'description', 'quantity',
            'price', 'created_by', 'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(float(data['price']), 10.99)
        self.assertEqual(data['quantity'], 100)


class ProductViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
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

    def test_update_own_product_success(self):
        view = ProductUpdateView()
        view.request = self.factory.put('/')
        view.request.user = self.user
        
        view.get_object = lambda: self.product
        
        serializer = ProductSerializer(self.product, data={'name': 'Updated'}, partial=True)
        self.assertTrue(serializer.is_valid())
        
        try:
            view.perform_update(serializer)
        except PermissionDenied:
            self.fail("perform_update raised PermissionDenied unexpectedly")

    def test_update_other_user_product_fails(self):
        view = ProductUpdateView()
        view.request = self.factory.put('/')
        view.request.user = self.other_user
        
        view.get_object = lambda: self.product
        
        serializer = ProductSerializer(self.product, data={'name': 'Updated'}, partial=True)
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(PermissionDenied) as context:
            view.perform_update(serializer)
        
        self.assertIn('You can only update your own products', str(context.exception))

    def test_delete_own_product_success(self):
        view = ProductDeleteView()
        view.request = self.factory.delete('/')
        view.request.user = self.user
        
        try:
            view.perform_destroy(self.product)
        except PermissionDenied:
            self.fail("perform_destroy raised PermissionDenied unexpectedly")
        
        self.assertFalse(Products.objects.filter(product_id=self.product.product_id).exists())

    def test_delete_other_user_product_fails(self):
        view = ProductDeleteView()
        view.request = self.factory.delete('/')
        view.request.user = self.other_user
        
        with self.assertRaises(PermissionDenied) as context:
            view.perform_destroy(self.product)
        
        self.assertIn('You can only delete your own products', str(context.exception))
        
        self.assertTrue(Products.objects.filter(product_id=self.product.product_id).exists())

    def test_product_creation_with_user(self):
        from .views.product_views import ProductListCreateView
        
        view = ProductListCreateView()
        view.request = self.factory.post('/')
        view.request.user = self.user
        
        data = {
            'name': 'View Created Product',
            'description': 'Created through view',
            'price': 25.99,
            'quantity': 30
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        view.perform_create(serializer)
        
        created_product = Products.objects.get(name='View Created Product')
        self.assertEqual(created_product.created_by, self.user)
        self.assertEqual(created_product.description, 'Created through view')
        self.assertEqual(float(created_product.price), 25.99)
        self.assertEqual(created_product.quantity, 30)
        
