from rest_framework import permissions


class IsSeller(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == request.user.is_seller


class IsSellerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_seller:
            if view.action in ['create', 'update', 'partial_update', 'destroy']:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        return request.user == request.user.is_seller or request.user.is_staff
