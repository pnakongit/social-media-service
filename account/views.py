from rest_framework import generics
from rest_framework.permissions import AllowAny

from account.serializers import UserCreateSerializer


class UserCreateApiView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
