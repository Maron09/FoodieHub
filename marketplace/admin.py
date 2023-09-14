from django.contrib import admin
from .models import *


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'fooditems', 'quantity', 'updated_at')



admin.site.register(Cart, CartAdmin)

