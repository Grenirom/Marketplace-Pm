from celery import shared_task
from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from account.models import password_reset_token_created
from .celery import app
from account.send_mail import send_confirmation_email


HOST = 'localhost:8000'


@app.task
def send_confirmation_email_task(user, code):
    send_confirmation_email(user, code)
