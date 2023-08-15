from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


from . import serializers
from .models import Article
from .permissions import IsAuthorOrAdmin, IsAuthor


class StandartResultPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all().order_by('id')
    pagination_class = StandartResultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title', 'body')
    filterset_fields = ('owner', )
    # permission_classes = [IsAuthorOrAdmin, ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ArticleListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return serializers.ArticleCreateSerializer
        return serializers.ArticleDetailSerializer

    def get_permissions(self):
        # удалять может только автор поста либо админы
        if self.action == 'destroy':
            return [IsAuthorOrAdmin(), ]
        # обновлять может только автор поста
        elif self.action in ('update', 'partial_update'):
            return [IsAuthor(), ]
        # просматривать могут все (list, retrive),
        # но создавать может только залогиненный пользователь
        return [permissions.IsAuthenticatedOrReadOnly(), ]

