from django.contrib import admin

from product.models import Product, ProductImage, Favorite, Likes


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    model = Favorite
    fields = ('user', 'product', 'favorite')


@admin.register(Likes)
class FavoriteAdmin(admin.ModelAdmin):
    model = Likes
    fields = ('user', 'product', 'is_liked')


class ImageInLineAdmin(admin.TabularInline):
    model = ProductImage
    fields = ('image',)
    max_num = 5


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInLineAdmin, ]
