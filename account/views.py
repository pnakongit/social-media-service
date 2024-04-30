from typing import Any

from django.contrib.auth import login
from knox.views import LoginView, LogoutView as KnoxLogoutView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from account.serializers import UserCreateSerializer, AuthTokenSerializer


class UserCreateApiView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a new user."""
        return super().post(request, *args, **kwargs)


class LoginApiView(LoginView):
    permission_classes = [AllowAny]
    serializer_class = AuthTokenSerializer

    def post(self, request: Request, format=None) -> Response:
        """Obtain an access token and save it into the database"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super().post(request, format)


class LogoutView(KnoxLogoutView):

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete an auth token for the user"""
        return super().post(request, *args, **kwargs)
