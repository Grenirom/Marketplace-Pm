from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import SellerProfile
from .permissions import IsAuthorOrAdmin
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from account import serializers
from account.send_mail import send_confirmation_email
from django.db.models.signals import post_save
from django.dispatch import receiver

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
                send_confirmation_email(user.email, user.activation_code)
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


class Login(TokenObtainPairView):
    permission_classes = (permissions.AllowAny, )


class Refresh(TokenRefreshView):
    permission_classes = (permissions.AllowAny, )

    # @cache_page(60 * 15)
    # @action(['GET'], detail=True)
    # def favorites(self, request, pk):
    #     product = self.get_object()
    #     favorites = product.favorites.filter(favorite=True)
    #     serializer = FavoriteListSerializer(instance=favorites, many=True)
    #     return Response(serializer.data, status=200)


class SellerApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_seller_pending:
            return Response({"message": "Your seller application is already pending."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_seller_pending = True
        user.save()

        # Create a SellerProfile instance
        seller_data = {
            "user": user,
            "store_name": request.data.get("store_name", ""),
            "description": request.data.get("description", ""),
            "website": request.data.get("website", ""),
            "social_media": request.data.get("social_media", ""),
            "country": request.data.get("country", ""),
            "city": request.data.get("city", ""),
            "tin": request.data.get("tin", ""),
            "checking_account": request.data.get("checking_account", ""),
            "bank_identification_code": request.data.get("bank_identification_code", ""),
            "tax_registration_reason_code": request.data.get("tax_registration_reason_code", "")
        }

        serializer = serializers.SellerSerializer(data=seller_data)
        print(seller_data, '************************* THIS IS A SELLER DATA')
        if serializer.is_valid():
            serializer.save()

        return Response({"message": "Your seller application has been submitted."},
                        status=status.HTTP_200_OK)


class ApproveSellerView(APIView):
    permission_classes = [permissions.IsAdminUser, ]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"message": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

        if not user.is_seller_pending:
            return Response({"message": "User's seller application is not pending approval."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_seller_pending = False
        user.is_seller = True
        user.save()

        # Используем данные из запроса и создаем запись в модели SellerProfile
        serializer = serializers.SellerSerializer(data=request.data)
        print(request.data, '!!!!!!!!!!!!!!!!!!!!')
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "Seller approved and SellerProfile created."},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateViewSet(UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserUpdateSerializer
    permission_classes = (IsAuthorOrAdmin,)


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)


class RefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
