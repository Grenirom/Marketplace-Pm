from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

    class Meta:
        model = Category
        fields = ['slug', 'name', 'photo', 'description', 'parent']

    # def to_representation(self, instance):
    #     repr = super().to_representation(instance)
    #     children = instance.children.all()
    #     if children:
    #         repr['children'] = CategorySerializer(children, many=True).data
    #     return repr
