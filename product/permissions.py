from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if view.action in ['create', 'update', 'partial_update', 'destroy']:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user.is_staff


# class IsOwnerOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # Разрешаем GET, HEAD или OPTIONS запросы для всех пользователей
#         if request.method in SAFE_METHODS:
#             return True
#
#         # Разрешаем PUT и PATCH запросы только самому пользователю
#         return obj == request.user
