from django.urls import path
from . import views


urlpatterns = [
    path('registerUser/', views.registerUser, name='register-user'),
    path('registerVendor/', views.registerVendor, name='register-vendor'),
    
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('myAccount/', views.myAccount, name='my-account'),
    path('customerDashboard/', views.customerDashboard, name='customer-dashboard'),
    path('vendorDashboard/', views.vendorDashboard, name='vendor-dashboard'),
]