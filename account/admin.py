from django.contrib import admin

from account.models import CustomUser, SellerProfile

admin.site.register(CustomUser)


class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'store_name', 'description', 'website']


admin.site.register(SellerProfile, SellerProfileAdmin)