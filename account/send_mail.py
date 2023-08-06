from django.core.mail import send_mail

HOST = 'localhost:8000'


def send_confirmation_email(user, code):
    link = f'http://{HOST}/api/v1/accounts/activate/{code}/'
    send_mail(
        'Здравствуйте, активируйте ваш аккаунт!',
        f'Чтобы активировать ваш аккаунт нужно перейти по ссылке ниже:'
        f'\n{link}'
        f'\nСсылка работает один раз!',
        'kochemarov@gmail.com',
        [user],
        fail_silently=False,
    )


def send_notification(user_email, order_id, price):
    send_mail(
        'Уведомление о создании заказа!',
        f'''Вы создали заказ №{order_id}, ожидайте звонка!
            Полная стоимость вашего заказа: {price}.
            Спасибо за то что выбрали нас!''',
        'from@exmple.com',
        [user_email],
        fail_silently=False
    )
