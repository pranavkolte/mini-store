from django.urls import path
from .views import CreatePaymentView, CartTotalView

urlpatterns = [
    path('create/', CreatePaymentView.as_view(), name='create-payment'),
    path('cart-total/', CartTotalView.as_view(), name='cart-total'),
]