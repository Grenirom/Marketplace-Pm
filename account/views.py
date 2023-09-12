from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from config.tasks import send_confirmation_email_task
from product.serializers import FavoriteListSerializer
from .models import SellerProfile
from .permissions import IsAuthorOrAdmin
from account import serializers

User = get_user_model()


class UserViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)

    @action(['POST'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_email_task.delay(user.email, user.activation_code)
            except Exception as e:
                return Response({'msg': 'Registered, but troubles with email!',
                                 'data': serializer.data}, status=201)
        return Response(serializer.data, status=201)

    @action(['GET'], detail=False, url_path='activate/(?P<uuid>[0-9A-Fa-f-]+)')
    def activate(self, request, uuid):
        try:
            user = User.objects.get(activation_code=uuid)
        except User.DoesNotExist:
            return Response({'msg': 'Invalid link, or link has already expired!'}, status=400)
        user.is_active = 'True'
        user.activation_code = ''
        user.save()
        return Response({'msg': 'Successfully activated your account!'}, status=200)

    # @cache_page(60 * 15)
    @action(['GET'], detail=True)
    def favorites(self, request, pk):
        product = self.get_object()
        favorites = product.favorites.filter(favorite=True)
        serializer = FavoriteListSerializer(instance=favorites, many=True)
        return Response(serializer.data, status=200)


class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)


class RefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny,)


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthorOrAdmin, ]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)  # Фильтруем по текущему пользователю

    @action(detail=False, methods=['GET'])
    def my_profile(self, request):
        profile = self.get_queryset().first()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['PUT', 'PATCH'])
    def update_my_profile(self, request):
        profile = self.get_queryset().first()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SellerProfileCreateView(generics.CreateAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = serializers.SellerSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_seller_pending:
            return Response({"message": "Your seller application is already pending."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_seller_pending = True
        user.save()

        serializer.save(user=user)


class SellerProfileViewSet(viewsets.ModelViewSet):
    queryset = SellerProfile.objects.all()
    serializer_class = serializers.SellerSerializer
    permission_classes = [IsAuthorOrAdmin, ]

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request):
        profile = self.queryset.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(['PUT', 'PATCH'], detail=True)
    def update_profile(self, request, pk=None):
        profile = self.queryset.get(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ApproveSellerView(APIView):
    permission_classes = [permissions.IsAdminUser, ]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"message": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

        if not user.is_seller_pending:
            return Response({"message": "Application was not found!"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_seller_pending = False
        user.is_seller = True
        user.save()

        return Response({"message": "Seller approved."}, status=status.HTTP_200_OK)


class SellerAllView(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_seller_pending=True)
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.SellerAdminListSerializer
        elif self.action == 'retrieve':
            return serializers.SellerProfileUpdateSerializer
        else:
            raise serializers.ValidationError({"detail": "Method not allowed"})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())  # Применяем фильтры
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user_instance = self.get_object()

        try:
            seller_profile_instance = SellerProfile.objects.get(user=user_instance)
            serializer = self.get_serializer(seller_profile_instance)
            return Response(serializer.data)
        except SellerProfile.DoesNotExist:
            return Response({"detail": "Profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
