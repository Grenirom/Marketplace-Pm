from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework import generics
# from mainapp.tasks import send_activation_mail_task
from . import serializers
from .send_email import send_activation_mail

User = get_user_model()


class AccountViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.AllowAny, ]

    @swagger_auto_schema(request_body=serializers.RegisterSerializer)
    @action(['POST'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_activation_mail(user.email, user.activation_code)
            except Exception as e:
                print(e, '@@@@@@@@@@')
                return Response({'msg': 'Registered, but issues with email',
                                 'data': serializer.data}, status=200)
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