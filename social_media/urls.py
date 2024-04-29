from django.urls import path
from rest_framework import routers

from social_media.views import (
    UserProfileViewSet,
    UserManageApiView,
    FollowerApiView,
    FollowingApiView,
)

router = routers.DefaultRouter()
router.register("user-profiles", UserProfileViewSet, basename="user_profiles")

urlpatterns = [
    path("user-profiles/me/", UserManageApiView.as_view(), name="manage_user_profile"),
    path(
        "user-profiles/me/followers/",
        FollowerApiView.as_view(),
        name="manage_user_profile_followers",
    ),
    path(
        "user-profiles/me/followings/",
        FollowingApiView.as_view(),
        name="manage_user_profile_followings",
    ),
] + router.urls

app_name = "social_media"
