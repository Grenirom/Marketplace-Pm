from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
import phonenumbers

from account.managers import MyManager


class CustomUser(AbstractUser):
    email = models.EmailField(_("email"), unique=True)
    first_name = models.CharField(_("first_name"), max_length=120)
    last_name = models.CharField(_("last_name"), max_length=120)
    username = models.CharField(_("username"), max_length=120, blank=True)
    password = models.CharField(_("password"), max_length=123)
    activation_code = models.CharField(_("activation_code"), max_length=255, blank=True)
    is_active = models.BooleanField(_("active"), default=False)
    image = models.ImageField(upload_to='images')

    objects = MyManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def create_activation_code(self):
        code = str(uuid4())
        self.activation_code = code


class SellerUser(CustomUser):
    address = models.CharField(_("address"), max_length=265)
    store_name = models.CharField(_("name"), max_length=123)
    phone_number = models.CharField(max_length=20, unique=True)
    inn = models.PositiveSmallIntegerField()

    def save(self, *args, **kwargs):
        # При сохранении пользователя, проверяем и форматируем номер телефона
        try:
            parsed_number = phonenumbers.parse(self.phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number")
            self.phone_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number")

        super().save(*args, **kwargs)

