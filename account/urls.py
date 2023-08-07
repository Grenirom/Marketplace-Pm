from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account import views
from account.views import AccountViewSet

router = DefaultRouter()
router.register('', AccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('refresh/', views.Refresh.as_view()),
    path('login/', views.Login.as_view())
]