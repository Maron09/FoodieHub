from django.shortcuts import render

# Create your views here.

def vendorProfile(request):
    return render(request, 'vendor/v_profile.html')