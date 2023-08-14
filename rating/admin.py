from django.contrib import admin

from rating.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    model = Review
    fields = ('user', 'product', 'rating', 'text')