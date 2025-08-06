from django.urls import path
from .views import CreateOrderView, ListOrderView, DeleteOrderView

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('list/', ListOrderView.as_view(), name='list-orders'),
    path('delete/<uuid:pk>/', DeleteOrderView.as_view(), name='delete-order'),
]