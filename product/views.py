from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status, response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# from rating.serializers import ReviewActionSerializer
from . import serializers
from .models import Product, ProductImage, Likes, Favorite
from .permissions import IsAuthorOrAdmin
# from .permissions import IsAuthorOrAdmin, IsAuthor
from .serializers import ProductSerializer


class StandartResultPagination(PageNumberPagination):
    page_size = 12
    page_query_param = 'page'


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    pagination_class = StandartResultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title', 'description')
    filterset_class = ProductFilter
    filterset_fields = ('title', 'owner', 'category', 'type', 'release_date',
                        'brand', 'manufacturer', 'release_date')

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q')

        if search_query:
            queryset = queryset.filter(title__icontains=search_query) | queryset.filter(
                description__icontains=search_query)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ProductListSerializer
        return serializers.ProductSerializer

    def get_permissions(self):
        if self.action in ('toggle_like', 'toggle_favorites', 'reviews'):
            return [permissions.IsAuthenticatedOrReadOnly(), ]
        elif self.action in ('list', 'retrieve'):
            return [permissions.AllowAny(), ]
        return [IsAuthorOrAdmin(), ]

    # @method_decorator(cache_page(60))  # Кеширование на 1 минуту
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def toggle_like(self, request, pk):
        product = self.get_object()
        user = request.user
        like_obj, created = Likes.objects.get_or_create(product=product, user=user)

        like_obj.is_liked = not like_obj.is_liked
        like_obj.save()
        return Response('like toggled')

    # api/v1/products/id/toggle_favorites/
    @action(detail=True, methods=['GET'])
    def toggle_favorites(self, request, pk):
        product = self.get_object()
        user = request.user
        fav, created = Favorite.objects.get_or_create(product=product, user=user)

        fav.favorite = not fav.favorite
        fav.save()
        return Response('favourite toggled')

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('likes_from', openapi.IN_QUERY, 'filter products by amount of likes', True,
                          type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["GET"])
    def likes(self, request, pk=None):
        from django.db.models import Count
        q = request.query_params.get("likes_from")  # request.query_params = request.GET
        queryset = self.get_queryset()
        queryset = queryset.annotate(Count('likes')).filter(likes__count__gte=q)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {'request': self.request}

    # api/v1/products/<id>/reviews/
    # @action(['GET', 'POST'], detail=True)
    # def reviews(self, request, pk):
    #     product = self.get_object()
    #     if request.method == 'GET':
    #         reviews = product.reviews.all()
    #         serializer = ReviewActionSerializer(reviews, many=True).data
    #         return response.Response(serializer, status=200)
    #     else:
    #         if product.reviews.filter(user=request.user).exists():
    #             return response.Response('You already reviewed this product!',
    #                                      status=400)
    #         data = request.data  # rating text
    #         serializer = ReviewActionSerializer(data=data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(user=request.user, product=product)
    #         return response.Response(serializer.data, status=201)
    #
    # # api/v1/product/id/
    # @action(['DELETE'], detail=True)
    # def review_delete(self, request, pk):
    #     product = self.get_object()  # Product.objects.get(id=pk)
    #     user = request.user
    #     if not product.reviews.filter(user=user).exists():
    #         return response.Response('You didn\'t reviewed this product!',
    #                                  status=400)
    #     review = product.reviews.get(user=user)
    #     review.delete()
    #     return response.Response('Successfully deleted', status=204)
