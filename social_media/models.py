from django.contrib.auth import get_user_model
from django.db import models

from social_media.helpers import upload_image_file_path

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    username = models.CharField(max_length=25, unique=True)
    bio = models.TextField()
    profile_picture = models.ImageField(
        upload_to=upload_image_file_path, blank=True, null=True
    )
    followers = models.ManyToManyField(
        "UserProfile", related_name="followings", blank=True
    )

    class Meta:
        ordering = ("user",)

    def __str__(self) -> str:
        return self.username


class Post(models.Model):
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    image = models.ImageField(upload_to=upload_image_file_path)
    likes = models.ManyToManyField(UserProfile, related_name="liked_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Post {self.id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Comment {self.id}"
