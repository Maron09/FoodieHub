from django.contrib import admin
from .models import *




class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name','is_approved', 'created_at')
    list_display_links = ('vendor_name','user')
    list_editable = ('is_approved',)



admin.site.register(Vendor, VendorAdmin)
