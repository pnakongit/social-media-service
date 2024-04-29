from rest_framework.permissions import BasePermission


class HasUserProfile(BasePermission):
    message = "You don't have a user profile"

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and request.user.is_authenticated and request.user.has_profile
        )
