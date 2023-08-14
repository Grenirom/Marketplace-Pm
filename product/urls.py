from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import ProductViewSet

router = DefaultRouter()
router.register('', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
