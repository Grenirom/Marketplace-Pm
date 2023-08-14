from django.db.models import Avg, Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from decouple import config

# from rating.models import Review
from .models import Product, ProductImage, Likes, Favorite
from category.models import Category


class RecommendedProductSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'rating', 'preview')


class SimilarProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'preview')


class ProductListSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')
    category_name = serializers.ReadOnlyField(source='category.name')
    parent = serializers.ReadOnlyField(source='category.parent.slug')

    class Meta:
        model = Product
        fields = ('id', 'owner', 'owner_email', 'category_name', 'parent', 'title',
                  'price', 'preview')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    owner_email = serializers.ReadOnlyField(source='owner.email')
    owner = serializers.ReadOnlyField(source='owner.id')
    parent = serializers.ReadOnlyField(source='category.parent.slug')
    similar_products = serializers.SerializerMethodField()
    recommended_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'owner', 'owner_email', 'title', 'description', 'category', 'parent',
            'price', 'quantity', 'brand', 'length', 'width', 'height', 'manufacturer',
            'type', 'country_of_origin', 'release_date', 'created_at', 'updated_at',
            'preview', 'images', 'similar_products', 'recommended_products'
        )

    def get_similar_products(self, obj):
        similar_products = Product.objects.filter(title__icontains=obj.title.split()[0]).exclude(id=obj.id)[:5]
        serializer = SimilarProductSerializer(similar_products, many=True)
        return serializer.data

    @staticmethod
    def get_avg_r(product):
        return product.reviews.aggregate(Avg('rating'))['rating__avg']

    def get_recommended_products(self, instance):
        products = Product.objects.all()
        ls = []
        for product in products:
            avg_rating = self.get_avg_r(product)
            if avg_rating is not None:
                data = {
                    'id': product.id,
                    'title': product.title,
                    'rating': avg_rating,
                    'preview': product.preview,
                }
                ls.append(data)

        recommended_products = sorted(ls, key=lambda x: x['rating'], reverse=True)[:5]
        serializer = RecommendedProductSerializer(recommended_products, many=True)
        return serializer.data

    @staticmethod
    def get_stars(instance):
        stars = {
            '5': instance.reviews.filter(rating=5).count(), '4': instance.reviews.filter(rating=4).count(),
            '3': instance.reviews.filter(rating=3).count(), '2': instance.reviews.filter(rating=2).count(),
            '1': instance.reviews.filter(rating=1).count()}
        return stars

    def to_representation(self, instance):
        request = self.context.get('request')
        repr = super().to_representation(instance)
        repr['rating'] = instance.reviews.aggregate(Avg('rating'))
        rating = repr['rating']
        rating['ratings_count'] = instance.reviews.count()
        repr['stars'] = self.get_stars(instance)
        repr['likes_count'] = instance.likes.filter(is_liked=True).count()
        repr['liked_by_user'] = False
        repr['favorite_by_user'] = False
        if request:
            if request.user.is_authenticated:
                repr['liked_by_user'] = Likes.objects.filter(user=request.user, product=instance,
                                                             is_liked=True).exists()
                repr['favorite_by_user'] = Favorite.objects.filter(user=request.user, favorite=True,
                                                                   product=instance).exists()
        return repr

    def create(self, validated_data):
        request = self.context.get('request')
        images = request.FILES.getlist('images')
        product = Product.objects.create(**validated_data)

        count = 0
        for image in images:
            if count >= 5:
                break
            ProductImage.objects.create(image=image, product=product)
            count += 1

        return product


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Category
        fields = ('pk', 'name')


class FavoriteListSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(source='product.title')
    owner = serializers.ReadOnlyField(source='product.owner.email')
    category = CategorySerializer(source='product.category')
    price = serializers.ReadOnlyField(source='product.price')
    photo = serializers.ReadOnlyField(source='product.preview.url')
    # photo = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('category', 'id', 'owner', 'title', 'price', 'photo')


    def to_representation(self, instance):
        repr = super().to_representation(instance)
        # repr['photo'] = self.instance.preview.url
        repr['photo'] = f'{config("HOST")}{self.get_photo(instance)}'
        return repr

    def get_photo(self, instance):
        return instance.product.preview.url if instance.product.preview else None
