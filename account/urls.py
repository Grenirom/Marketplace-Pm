from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter
from account.views import UserViewSet
from .views import ChangePasswordView

router = SimpleRouter()
router.register('', UserViewSet)

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('refresh/', views.RefreshView.as_view()),
    path('', include(router.urls)),
    path('<int:pk>/', views.UserUpdateViewSet.as_view({'patch': 'update'})),
    path('change-password/', views.ChangePasswordView.as_view()),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

