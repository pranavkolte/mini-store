from django.urls import path
from products.views.product_views import (
    ProductListCreateView,
    ProductRetrieveView,
    ProductUpdateView,
    ProductDeleteView,
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<uuid:pk>/', ProductRetrieveView.as_view(), name='product-detail'),
    path('products/<uuid:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<uuid:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
]
