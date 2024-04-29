from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasUserProfile(BasePermission):
    message = "You don't have a user profile"

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and request.user.is_authenticated and request.user.has_profile
        )


class IsObjectOwner(BasePermission):
    message = "You are not an object owner"

    def has_object_permission(self, request, view, obj) -> bool:
        return request.method in SAFE_METHODS or obj.user_profile.user == request.user
