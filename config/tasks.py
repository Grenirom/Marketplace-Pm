from .celery import app
from account.send_mail import send_confirmation_email

HOST = 'localhost:8000'


@app.task
def send_confirmation_email_task(user, code):
    send_confirmation_email(user, code)

