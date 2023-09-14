from django.urls import path
from . import views


urlpatterns = [
    path('', views.marketPlace, name='marketplace'),
    
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),
    
    #Add tocart
    path('add_to_cart/<int:food_id>/',  views.addToCart, name='add_to_cart'),
    #Decrease cart
    path('decrease_cart/<int:food_id>' , views.decreaseCart, name='decrease_cart'),
    #delete from cart
    path('delete_cart/<int:cart_id>/', views.deleteItem, name='delete_cart'),
]