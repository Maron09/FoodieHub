from django import forms
from .models import *
from accounts.validators import *

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']


class ProductForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images])
    class Meta:
        model = Product
        fields = ['category', 'food_name', 'description', 'price', 'image', 'is_available']