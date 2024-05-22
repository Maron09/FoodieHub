from django.contrib import admin
from .models import *



class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)} #Generate the slug automatically
    list_display = ('category_name', 'vendor', 'updated_at')
    search_fields = ('category_name', 'vendor__vendor_name') #reason is vendor is a foreign key so we target the vendor name


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_name',)} #Generate the slug automatically
    list_display = ('food_name', 'category', 'vendor', 'price', 'is_available', 'updated_at')
    search_fields = ('food_name', 'category__category_name','vendor__vendor_name', 'price')
    list_filter = ('is_available', )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)