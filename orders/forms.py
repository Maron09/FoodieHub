from django import forms
from .models import *



class orderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'country', 'state', 'city', 'pin_code']