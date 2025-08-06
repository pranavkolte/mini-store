from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema

from .serializers import SignupSerializer, LoginSerializer

User = get_user_model()


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response(
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': str(user.id),
                'email': user.email,
            },
            status=status.HTTP_200_OK
        )