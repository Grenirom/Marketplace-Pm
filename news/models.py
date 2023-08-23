from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class News(models.Model):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT,
                              related_name='news')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', null=True)
    body = models.TextField()
    is_seller_news = models.BooleanField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'news'
        verbose_name_plural = 'news'

    def __str__(self):
        return f'{self.id} {self.title} {self.created_at}'
