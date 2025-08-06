from django.urls import path
from .views import SignupView, LoginView

urlpatterns = [
    path(route='signup/', view=SignupView.as_view(), name='signup'),
    path(route='login/', view=LoginView.as_view(), name='login'),
]