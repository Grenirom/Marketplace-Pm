from rest_framework import serializers
from .models import Category, CategoryPhoto


class CategoryPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryPhoto
        fields = ['id', 'photo_desc']


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)
    photos_desc = CategoryPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['slug', 'name', 'photo', 'description', 'parent', 'photos_desc']

    # def to_representation(self, instance):
    #     repr = super().to_representation(instance)
    #     children = instance.children.all()
    #     if children:
    #         repr['children'] = CategorySerializer(children, many=True).data
    #     return repr
