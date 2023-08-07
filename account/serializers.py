from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=20, required=True, write_only=True)
    password2 = serializers.CharField(min_length=8, max_length=20, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'image', 'username')

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs.pop('password2')
        if password2 != password:
            raise serializers.ValidationError("The passwords didn't match!")
        validate_password(password)
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
