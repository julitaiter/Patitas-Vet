from django.contrib.auth import logout as django_logout
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    CurrentUserSerializer,
    LoginSerializer,
    RegisterSerializer,
    TokenResponseSerializer,
)


def token_response(user, request):
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "usuario": CurrentUserSerializer(user, context={"request": request}).data,
    }


class RegisterView(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = RegisterSerializer

    @extend_schema(responses={status.HTTP_201_CREATED: TokenResponseSerializer})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(token_response(user, request), status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = LoginSerializer

    @extend_schema(responses={status.HTTP_200_OK: TokenResponseSerializer})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(token_response(user, request))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request):
        if request.auth is not None and hasattr(request.auth, "delete"):
            request.auth.delete()
        else:
            Token.objects.filter(user=request.user).delete()
            django_logout(request._request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user
