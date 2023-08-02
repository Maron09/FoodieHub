from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vendorProfile, name='v-profile'),
    path('menu_builder/', views.vendorMenuBuilder, name='menu_builder'),
    path('menu_builder/category/<int:pk>/', views.foodItem_by_cat, name='fooditem_by_cat'),
    
    
    #Category
    path('menu_builder/category/add/', views.addCategory, name='add_category'),
    path('menu_builder/category/edit/<int:pk>/', views.editCategory, name='edit_category'),
    path('menu_builder/category/delete/<int:pk>/', views.deleteCategory, name='delete_category'),
]