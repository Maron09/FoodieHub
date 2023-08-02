from .models import *


def get_vendor(request):
    vendor = Vendor.objects.get(user= request.user)
    return vendor