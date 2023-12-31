from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

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
    is_seller_pending = models.BooleanField(
        _("seller pending"),
        default=False,
        help_text=_("Indicates whether the user's seller application is pending approval."
                    "If True means pending, if False means not pending."
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


class SellerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    social_media = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    # Taxpayer Identification Number (ИНН)
    tin = models.PositiveBigIntegerField(
        validators=[
            RegexValidator(r'^\d{12}$', 'Enter a valid 12-digit number.')
        ]
    )
    checking_account = models.DecimalField(
        max_digits=20, decimal_places=0,
        validators=[
            MaxValueValidator(99999999999999999999),  # Максимальное значение на 20 цифр
            MinValueValidator(10000000000000000000)  # Минимальное значение на 20 цифр
        ]
    )
    bank_identification_code = models.PositiveBigIntegerField(
        validators=[
            RegexValidator(r'^\d{9}$', 'Enter a valid 9-digit number.')
        ]
    )
    tax_registration_reason_code = models.PositiveBigIntegerField(
        validators=[
            RegexValidator(r'^\d{9}$', 'Enter a valid 9-digit number.')
        ]
    )

    def __str__(self):
        return self.store_name


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}{}".format(reverse('password_reset:reset-password-request'),
                                            reset_password_token.key)
    # ?token=
    link = f'http://{HOST}{email_plaintext_message}'

    send_mail(
        # title:
        "Восстановление пароля для {title}".format(title="Mordo"),
        # message:
        f'Здравствуйте, восстановите ваш пароль!'
        f'\nЧтобы восстановить ваш пароль нужно скопировать код ссылки ниже и вставить его в поле на сайте:'
        f'\n{link}',
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email],
    )
