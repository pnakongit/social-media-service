from rest_framework import serializers

from social_media.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)
    follower_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "username", "bio", "profile_picture", "follower_count"]


class UserProfileCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserProfile
        fields = ["id", "user", "username", "bio", "profile_picture"]

    def create(self, validated_data: dict) -> UserProfile:

        if UserProfile.objects.filter(user=validated_data["user"]).exists():
            raise serializers.ValidationError("User profile is already registered")

        return super().create(validated_data)


class UserProfileUpdateSerializer(serializers.ModelSerializer):

    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "bio", "profile_picture"]


class UserProfileSortSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ["id", "username"]

        read_only_fields = ["id", "username"]