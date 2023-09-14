from django.db import models
from accounts.models import *
from menu.models import *


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditems = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.user
