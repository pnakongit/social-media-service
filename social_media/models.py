from django.contrib.auth import get_user_model
from django.db import models, transaction

from social_media.helpers import upload_image_file_path

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField()
    profile_picture = models.ImageField(upload_to=upload_image_file_path)
    followers = models.ManyToManyField(
        "UserProfile", related_name="followings", blank=True
    )

    class Meta:
        ordering = ("user",)

    def __str__(self) -> str:
        return f"User profile ID {self.pk}"


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


class PostponedPost(models.Model):
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="postponed_posts"
    )
    content = models.TextField()
    image = models.ImageField(upload_to=upload_image_file_path)
    postponed_at = models.DateTimeField()
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ("-postponed_at",)

    def __str__(self) -> str:
        return f"Postponed post {self.id}"

    def publish(self) -> None:
        with transaction.atomic():
            Post.objects.create(
                user_profile=self.user_profile, content=self.content, image=self.image
            )
            self.published = True
            self.save()


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
