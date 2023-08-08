from rest_framework.permissions import BasePermission, IsAdminUser


class IsAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD или OPTIONS запросы для всех пользователей
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Разрешаем PATCH запросы только авторизованным пользователям, которые являются авторами объекта или администраторам
        return obj == request.user or IsAdminUser().has_permission(request, view)
