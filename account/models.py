from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
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
    is_seller = models.BooleanField(
        _("seller"),
        default=False,
        help_text=_(
            "If selected it user is approved seller. "
            "Unselect this if you want block seller."
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


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # saved_products = models.ManyToManyField(Product, blank=True, related_name='saved_by')
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)


class SellerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    social_media = models.CharField(max_length=255, blank=True, null=True)
    # Taxpayer Identification Number (ИНН)
    tin = models.PositiveBigIntegerField(
        validators=[
            MaxValueValidator(999999999999),  # Максимальное значение на 12 цифр
            MinValueValidator(100000000000)  # Минимальное значение на 12 цифр
        ],
        blank=True, null=True
    )
    checking_account = models.PositiveBigIntegerField(
        validators=[
            MaxValueValidator(99999999999999999999),  # Максимальное значение на 20 цифр
            MinValueValidator(10000000000000000000)  # Минимальное значение на 20 цифр
        ],
        blank=True, null=True
    )
    bank_identification_code = models.PositiveBigIntegerField(
        validators=[
            MaxValueValidator(999999999),  # Максимальное значение на 9 цифр
            MinValueValidator(100000000)  # Минимальное значение на 9 цифр
        ],
        blank=True, null=True
    )
    tax_registration_reason_code = models.PositiveBigIntegerField(
        validators=[
            MaxValueValidator(999999999),  # Максимальное значение на 9 цифр
            MinValueValidator(100000000)  # Минимальное значение на 9 цифр
        ],
        blank=True, null=True
    )


@receiver(reset_password_token_created)
@permission_classes([AllowAny, ])
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}{}".format(reverse('password_reset:reset-password-request'),
                                            reset_password_token.key)
    # ?token=
    link = f'http://{HOST}{email_plaintext_message}'

    send_mail(
        # title:
        "Восстановление пароля для {title}".format(title="Mordo"),
        # message:
        f'Здравствуйте, восстановите ваш пароль!\nЧтобы восстановить ваш пароль нужно перейти по ссылке ниже:\n'
        f'\n{link}',
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email],
    )
