from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from . import serializers
from .models import News
from .permissions import IsAdminUser, CanAccessSellerNews


class StandartResultPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'


class NewsViewSet(ModelViewSet):
    queryset = News.objects.all().order_by('id')
    pagination_class = StandartResultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title', 'body')
    filterset_fields = ('owner', 'is_seller_news')

    # permission_classes = [CanAccessNewsGroup, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q')

        if search_query:
            queryset = queryset.filter(title__icontains=search_query) | queryset.filter(
                body__icontains=search_query)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.NewsListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return serializers.NewsCreateSerializer
        return serializers.NewsDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'list', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser(), ]
        elif self.action == 'sellernews':
            return [CanAccessSellerNews(), ]
        return [permissions.AllowAny(), ]

    @action(detail=False, methods=['GET'])
    def sellernews(self, request):
        queryset = News.objects.filter(is_seller_news=True).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.AllowAny, ])
    def publicnews(self, request):
        queryset = News.objects.filter(is_seller_news=False).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
