from django.urls import path
from .views import AddToCartView, RemoveFromCartView, ListCartView

urlpatterns = [
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('remove/<uuid:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('list/', ListCartView.as_view(), name='list-cart'),
]