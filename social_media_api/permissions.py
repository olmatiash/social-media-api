from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            obj.created_by == request.user
            or request.method in ("GET", "HEAD", "OPTIONS", "POST")
        )


class IsOwnerOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj.created_by == request.user)
