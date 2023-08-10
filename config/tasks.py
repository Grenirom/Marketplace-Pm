from .celery import app
from account.send_mail import send_confirmation_email
from account.models import password_reset_token_created


@app.task
def send_confirmation_email_task(user, code):
    send_confirmation_email(user, code)
