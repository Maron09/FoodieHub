from django.urls import path
from . import views


urlpatterns = [
    path('registerUser/', views.registerUser, name='register-user'),
    path('registerVendor/', views.registerVendor, name='register-vendor'),
    
    #user and vendor interface
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('myAccount/', views.myAccount, name='my-account'),
    path('customerDashboard/', views.customerDashboard, name='customer-dashboard'),
    path('vendorDashboard/', views.vendorDashboard, name='vendor-dashboard'),
    
    #email verification
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    #forgot Password
    path('forgot_password/', views.forgotPassword, name='forgot-password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset-password-validate'),
    path('reset_password/', views.resetPassword, name='reset-password'),
]