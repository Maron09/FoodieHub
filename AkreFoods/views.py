from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import *
from marketplace.views import *
from .utils import *


def home(request):
    # using the maps api to get the nearby restaurants on the home page based on the user's location if specified
    if get_or_set_current_location(request) is not None:
        pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))
        
        vendors = Vendor.objects.filter(
            user_profile__locations__distance_lte=(pnt, D(km=100))
        ).annotate(distance=Distance("user_profile__locations", pnt)).order_by("distance")
        
        # to get the distance between the user's location and the vendor
        for v in vendors:
            v.kms = round(v.distance.km, 1)
    else:
        # it will just show all the restaurants
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)