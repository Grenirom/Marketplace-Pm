from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver

# from account.send_mail import send_notification
from config.tasks import send_notification_task

User = get_user_model()

STATUS_CHOICES = (
    ('open', 'Открыт'),
    ('in_proccess', 'В обработке'),
    ('closed', 'Закрыт')
)

DELIVERY_CHOICES = (
        ('pickup', 'Самовывоз'),
        ('courier', 'Курьерская доставка'),
    )
PAYMENT_CHOICES = (
        ('cash', 'Наличными'),
        ('bank_transfer', 'Банковский перевод'),
        ('money_transfer', 'Денежный перевод'),
        ('cash_on_delivery', 'Оплата курьеру на месте'),
    )


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders',
                             on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, through=OrderItem)
    address = models.CharField(max_length=255)
    number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    total_sum = models.DecimalField(max_digits=9, decimal_places=2,
                                    blank=True)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()

    def __str__(self):
        return f'{self.id} -> {self.user}'


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, *args, **kwargs):
    send_notification_task.delay(
        instance.user.email, instance.id, instance.total_sum
    )