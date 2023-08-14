from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from rest_framework import serializers
from . import models

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=20,
                                     required=True, write_only=True)
    password2 = serializers.CharField(min_length=8, max_length=20,
                                      required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name',
                  'avatar', 'username')

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


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class SellerSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.SellerProfile
        fields = '__all__'


class SellerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SellerProfile
        fields = ('store_name', 'description', 'website', 'social_media', 'country', 'city', 'tin', 'checking_account',
                  'bank_identification_code', 'tax_registration_reason_code')


class SellerAdminListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', )


class SellerAdminDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'bank_identification_code', 'tax_registration_reason_code')

