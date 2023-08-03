from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from .managers import UserManager

HOST = 'localhost:3000'


class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)
    password = models.CharField(max_length=255)
    activation_code = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    avatar = models.ImageField(upload_to='avatars', blank=True,
                               default='avatars/default_avatar.jpg')
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.email}'

    def create_activation_code(self):
        code = str(uuid4())
        self.activation_code = code


# @receiver(reset_password_token_created)
# @permission_classes([AllowAny, ])
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
#     email_plaintext_message = "{}{}".format(reverse('password_reset:reset-password-request'),
#                                                    reset_password_token.key)
#     # ?token=
#     link = f'http://{HOST}{email_plaintext_message}'
#
#     send_mail(
#         # title:
#         "Восстановление пароля для {title}".format(title="Some website title"),
#         # message:
#         f'Здравствуйте, восстановите ваш пароль!\nЧтобы восстановить ваш пароль нужно перейти по ссылке ниже:\n'
#         f'\n{link}',
#         # from:
#         "noreply@somehost.local",
#         # to:
#         [reset_password_token.user.email],
#     )
