from django.urls import path, include
from . import views
from accounts import views as AccountView


urlpatterns = [
    path('', AccountView.customerDashboard, name='customer'),
    path('profile/', views.customerProfile, name='c-profile')
]