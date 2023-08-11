from random import randint

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, Count

from category.models import Category
from ckeditor.fields import RichTextField
from decimal import Decimal

User = get_user_model()

TYPE_CHOICES = (
    ('electric', 'электрическое'),
    ('gas', 'газовое'),
    ('hybrid', 'гибридное')
)


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT,
                              related_name='products')
    code = models.CharField(max_length=50)
    title = models.CharField(max_length=150)
    description = RichTextField()
    category = models.ForeignKey(Category, related_name='products',
                                 on_delete=models.RESTRICT)
    brand = models.CharField(max_length=150, blank=True, null=True)
    length = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    manufacturer = models.CharField(max_length=180, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    country_of_origin = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=0)
    preview = models.ImageField(upload_to='images/', null=True)
    release_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images', blank=True, null=True)
    name = models.CharField(max_length=15, unique=True)

    def generate_name(self):
        return 'image' + str(randint(100000, 999999))

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.generate_name()
        super(ProductImage, self).save(*args, **kwargs)


class Likes(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='likes')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE, related_name='likes')

    is_liked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product} -> {self.user} -> {self.is_liked}'

    class Meta:
        verbose_name = 'like'
        verbose_name_plural = 'likes'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    favorite = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product} -> {self.user} -> {self.favorite}'
