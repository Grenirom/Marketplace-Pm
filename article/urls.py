from django.urls import path, include

from article import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', views.ArticleViewSet)

urlpatterns = [
    path('', include(router.urls))
]