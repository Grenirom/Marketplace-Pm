from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions
from . import serializers
from .models import Category, CategoryPhoto
from .serializers import CategoryPhotoSerializer


class CategoryPhotoListCreateView(generics.ListCreateAPIView):
    queryset = CategoryPhoto.objects.all()
    serializer_class = CategoryPhotoSerializer


class CategoryPhotoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CategoryPhoto.objects.all()
    serializer_class = CategoryPhotoSerializer


class CategoryCreateListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    lookup_field = 'slug'
    # permission_classes = (permissions.IsAdminUser, )

    # @method_decorator(cache_page(60))  # Кеширование на 1 минуту
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'GET':
            return permissions.AllowAny(),
        return permissions.IsAdminUser(),


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny(), ]
        return [permissions.IsAdminUser(), ]
