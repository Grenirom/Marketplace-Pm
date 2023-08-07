from django.core.mail import send_mail

HOST = '127.0.0.1:8000'


def send_activation_mail(user, code):
    link = f'http://{HOST}/account/activate/{code}/'
    send_mail(
        'Вас приветствует Orda!',
        'Для активации вашегo аккаунта вам требуется перейти по ссылке ниже:'
        f'\n{link}'
        f'\nСсылка действительна только 1 раз!',
        'ngrebnev17@gmail.com',
        [user],
        fail_silently=True
    )