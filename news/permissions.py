from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_staff) or request.user.is_superuser


class CanAccessSellerNews(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == 'sellernews':
            return request.user.is_seller

        return True