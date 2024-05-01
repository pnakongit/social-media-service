from django.urls import path
from rest_framework_nested import routers

from social_media.views import (
    UserProfileViewSet,
    UserManageApiView,
    FollowerApiView,
    FollowingApiView,
    PostViewSet,
    CommentViewSet,
    PostponedPostCreateApiView,
)

router = routers.DefaultRouter()
router.register("user-profiles", UserProfileViewSet, basename="user_profiles")
router.register("posts", PostViewSet, basename="post")

post_router = routers.NestedDefaultRouter(router, "posts", lookup="post")
post_router.register("comments", CommentViewSet, basename="post_comment")

urlpatterns = (
    [
        path(
            "user-profiles/me/",
            UserManageApiView.as_view(),
            name="manage_user_profile",
        ),
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
        path(
            "posts/create-postponed-post/",
            PostponedPostCreateApiView.as_view(),
            name="create_postponed_post",
        ),
    ]
    + router.urls
    + post_router.urls
)

app_name = "social_media"
