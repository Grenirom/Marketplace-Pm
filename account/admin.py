from django.contrib import admin

from account.models import CustomUser, SellerUser

admin.site.register(CustomUser)
admin.site.register(SellerUser)
