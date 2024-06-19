from django.urls import path
from . import views
from accounts import views as AccountView


urlpatterns = [
    path('', AccountView.customerDashboard, name='customer'),
    path('profile/', views.customerProfile, name='c-profile'),
    path('my_orders/', views.my_orders, name='customer_orders'),
    path('order_details/<int:order_number>/', views.orderDetails, name='order_details')
]