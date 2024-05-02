from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from social_media.models import UserProfile, Post, Comment, PostponedPost


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    follower_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "username", "bio", "profile_picture", "follower_count"]


class UserProfileCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserProfile
        fields = ["id", "user", "bio", "profile_picture"]

    def create(self, validated_data: dict) -> UserProfile:

        if UserProfile.objects.filter(user=validated_data["user"]).exists():
            raise serializers.ValidationError("User profile is already registered")

        return super().create(validated_data)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "bio", "profile_picture"]

    def update(self, instance: UserProfile, validated_data: dict) -> UserProfile:
        with transaction.atomic():
            user = instance.user
            user_data = validated_data.pop("user", None)
            if user_data is not None:
                user.username = user_data.get("username", user.username)
                user.save()

            return super().update(instance, validated_data)


class UserProfileShortSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "username"]


class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user_profile.user.username", read_only=True
    )
    count_likes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "username", "content", "image", "count_likes"]


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = ["id", "content", "image"]


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user_profile.user.username", read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "username", "content", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "content"]


class PostponedPostCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = PostponedPost
        fields = ["id", "content", "image", "postponed_at"]
