from django.urls import path, include

from news import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', views.NewsViewSet)

urlpatterns = [
    path('', include(router.urls))
]