from django.urls import path
from . import views


urlpatterns = [
    path('registerUser/', views.registerUser, name='register-user'),
    path('registerVendor/', views.registerVendor, name='register-vendor')
]