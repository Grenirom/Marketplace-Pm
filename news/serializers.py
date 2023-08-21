from rest_framework import serializers

from .models import News


class NewsListSerializer(serializers.ModelSerializer):
    body_preview = serializers.SerializerMethodField()
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = News
        fields = ('id', 'title', 'owner', 'owner_email', 'image', 'body_preview')

    def get_body_preview(self, obj):
        if len(obj.body) > 300:
            return obj.body[:300] + '...'  # Обрезаем и добавляем многоточие
        return obj.body


class NewsCreateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = News
        fields = '__all__'


class NewsDetailSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = News
        fields = ('id', 'title', 'owner', 'owner_email', 'image', 'body')
