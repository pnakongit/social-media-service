from typing import Type

from django.db.models import QuerySet, Count
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from social_media.models import UserProfile
from social_media.permissions import HasUserProfile

from social_media.serializers import (
    UserProfileSerializer,
    UserProfileCreateSerializer,
    UserProfileUpdateSerializer,
    UserProfileSortSerializer,
)


class UserProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "create":
            return UserProfileCreateSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        profile_qs = (
            UserProfile.objects.select_related("user")
            .annotate(follower_count=Count("followers"))
            .order_by("id")
        )

        query_username = self.request.query_params.get("username")
        if query_username:
            profile_qs = profile_qs.filter(username=query_username)

        return profile_qs

    @action(
        detail=True,
        methods=["POST"],
        url_path="follow",
        url_name="follow",
        permission_classes=[HasUserProfile],
    )
    def follow(self, request, pk=None) -> Response:
        user_profile = self.get_object()
        follower_profile = request.user.profile

        if user_profile == follower_profile:
            return Response(
                {"detail": "You cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_profile.followers.add(follower_profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
        url_path="unfollow",
        url_name="unfollow",
        permission_classes=[HasUserProfile],
    )
    def unfollow(self, request, pk=None) -> Response:
        user_profile = self.get_object()
        follower_profile = request.user.profile

        user_profile.followings.remove(follower_profile)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserManageApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasUserProfile]

    def get_serializer_class(self) -> Type[Serializer]:
        if self.request.method in ["PUT", "PATCH"]:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_object(self) -> UserProfile:
        return UserProfile.objects.annotate(follower_count=Count("followers")).get(
            user=self.request.user
        )


class FollowerApiView(generics.ListAPIView):
    permission_classes = [HasUserProfile]
    serializer_class = UserProfileSortSerializer

    def get_queryset(self) -> QuerySet:
        follower_qs = self.request.user.profile.followers.all()
        return follower_qs


class FollowingApiView(generics.ListAPIView):
    permission_classes = [HasUserProfile]
    serializer_class = UserProfileSortSerializer

    def get_queryset(self) -> QuerySet:
        follower_qs = self.request.user.profile.followings.all()
        return follower_qs
