from django.core.mail import send_mail

HOST = 'localhost:8000'


def send_confirmation_email(user, code):
    link = f'http://{HOST}/accounts/activate/{code}/'
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
        'Вас приветствует TextileArt!',
        f'''Вы создали заказ №{order_id}, в скором времени наш менеджер свяжется с вами!
            Полная стоимость вашего заказа составила: {price}.
            Спасибо за доверие!''',
        'from@exmple.com',
        [user_email],
        fail_silently=False
    )
