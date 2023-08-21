from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


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
        if request.user.is_superuser or request.user.is_staff:
            return True
        return request.user == obj.owner and request.user.is_seller


# class IsOwnerOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # Разрешаем GET, HEAD или OPTIONS запросы для всех пользователей
#         if request.method in SAFE_METHODS:
#             return True
#
#         # Разрешаем PUT и PATCH запросы только самому пользователю
#         return obj == request.user
