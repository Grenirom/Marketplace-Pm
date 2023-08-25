from .celery import app
from account.send_mail import send_confirmation_email, send_notification

HOST = 'localhost:8000'


@app.task
def send_confirmation_email_task(user, code):
    send_confirmation_email(user, code)

@app.task
def send_notification_task(user_email, order_id, price):
    send_notification(user_email, order_id, price)
