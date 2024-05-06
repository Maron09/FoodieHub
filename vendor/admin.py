from django.contrib import admin
from .models import *




class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name','is_approved', 'created_at')
    list_display_links = ('vendor_name','user')
    list_editable = ('is_approved',)

class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'day', 'from_hour', 'to_hour')

admin.site.register(Vendor, VendorAdmin)
admin.site.register(Opening_hour, OpeningHourAdmin)
