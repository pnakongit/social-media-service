from typing import Type, Any

from django.db.models import QuerySet, Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from social_media.filters import HashtagSearchBackend
from social_media.models import UserProfile, Post, Comment
from social_media.permissions import HasUserProfile, IsObjectOwner

from social_media.serializers import (
    UserProfileSerializer,
    UserProfileCreateSerializer,
    UserProfileUpdateSerializer,
    UserProfileSortSerializer,
    PostSerializer,
    PostCreateUpdateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                description="The username of the user",
                required=False,
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Return a list of all profiles.
        Can be filtered by username.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Return a single profile."""
        return super().retrieve(request, *args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a new profile.
        Authenticated users can create one profiles.
        """
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        description="Authenticated user with userprofile follow to userprofile",
    )
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

    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        description="Authenticated user with userprofile unfollow from userprofile",
    )
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
        user_profile.followers.remove(follower_profile)

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

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieve authenticated user's profile"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update authenticated user's profile"""
        return super().update(request, *args, **kwargs)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update authenticated user's profile"""
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete authenticated user's profile"""
        return super().partial_update(request, *args, **kwargs)


class FollowerApiView(generics.ListAPIView):
    permission_classes = [HasUserProfile]
    serializer_class = UserProfileSortSerializer

    def get_queryset(self) -> QuerySet:
        follower_qs = self.request.user.profile.followers.all()
        return follower_qs

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return user profile list of followers"""
        return super().list(request, *args, **kwargs)


class FollowingApiView(generics.ListAPIView):
    permission_classes = [HasUserProfile]
    serializer_class = UserProfileSortSerializer

    def get_queryset(self) -> QuerySet:
        follower_qs = self.request.user.profile.followings.all()
        return follower_qs

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return user profile list of followings"""
        return super().list(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [HasUserProfile, IsObjectOwner]
    filter_backends = [HashtagSearchBackend]

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateUpdateSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        post_qs = Post.objects.filter(
            Q(user_profile__user=self.request.user)
            | Q(user_profile__followers=self.request.user.profile)
        )
        if self.request.method == "GET":
            post_qs = (
                post_qs.prefetch_related("user_profile", "likes")
                .annotate(count_likes=Count("likes"))
                .order_by("-id")
            )

        return post_qs

    def perform_create(self, serializer: Serializer) -> Post:
        return serializer.save(user_profile=self.request.user.profile)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="hashtags",
                description="hashtags",
                required=False,
                location=OpenApiParameter.QUERY,
                many=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Return a list of own posts and posts of user profiles they are following.
        Post can be filtered by hashtags
        """
        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a new post of user profile"""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a post detail"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update own post"""
        return super().update(request, *args, **kwargs)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update own post"""
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete own post"""
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        description="Like the post",
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        url_name="like",
        permission_classes=[HasUserProfile],
    )
    def like(self, request: Request, pk: int = None) -> Response:
        user_profile = self.get_object()
        user_profile.likes.add(request.user.profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        description="Unlike the post",
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="unlike",
        url_name="unlike",
        permission_classes=[HasUserProfile],
    )
    def unlike(self, request: Request, pk: int = None) -> Response:
        user_profile = self.get_object()
        user_profile.likes.remove(request.user.profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=None,
        description="Return a list of liked posts",
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="liked_post",
        url_name="liked_post",
    )
    def liked_post(self, request: Request) -> Response:
        post_qs = self.get_queryset().filter(likes=request.user.profile)
        serializer = self.get_serializer(post_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [HasUserProfile, IsObjectOwner]

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["create", "update", "partial_update"]:
            return CommentCreateSerializer
        return CommentSerializer

    def get_post(self) -> Post:
        post_qs = Post.objects.filter(
            Q(user_profile__user=self.request.user)
            | Q(user_profile__followers=self.request.user.profile)
        )
        return get_object_or_404(post_qs, pk=self.kwargs.get("post_pk"))

    def get_queryset(self) -> QuerySet:
        return Comment.objects.filter(post=self.get_post())

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(
            user_profile=self.request.user.profile,
            post=self.get_post(),
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a list of post comments"""
        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Add a comment to the post"""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a comment of the post"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update own comment of the post"""
        return super().update(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete own comment of the post"""
        return super().destroy(request, *args, **kwargs)
