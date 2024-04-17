from rest_framework import permissions


class IsAuthorModerAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            (request.method in permissions.SAFE_METHODS)
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.user.role != 'user'
                or request.method in permissions.SAFE_METHODS)


class IsModeratorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and
                request.user.role in ['moderator', 'admin'])
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and
                request.user.role in ['moderator', 'admin'])
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and
                request.user.role == 'admin')
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and
                request.user.role == 'admin')
        )


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin'
