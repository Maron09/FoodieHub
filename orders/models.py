from django.db import models
from accounts.models import *
from menu.models import *
import simplejson as json



request_object = ''

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('RazorPay', 'RazorPay'), # only available for indians
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=20)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=300)
    country = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    pin_code = models.CharField(max_length=15)
    total = models.FloatField()
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type' : {'tax_percentage' : 'tax_amount'}}", null=True) #because of multiple taxes
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=30)
    status = models.CharField(choices=STATUS, max_length=30, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    # To concatenate first and last name
    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'
    
    def order_placed_to(self):
        return ", ".join([str(i) for i in self.vendors.all()])
    
    def get_total_by_vendor(self):
        subtotal = 0
        tax = 0
        tax_dict = {}
        vendor = Vendor.objects.get(user=request_object.user)
        
        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id))
            
            for key, value in data.items():
                subtotal += float(key)
                value = value.replace("'", '"')
                value = json.loads(value)
                tax_dict.update(value)

                # calculate the tax
                # {'VAT': {'2.58': '0.27'}, 'CGT': {'2.00': '0.21'}
                for i in value:
                    for j in value[i]:
                        tax += float(value[i][j])
        grand_total = float(subtotal) + float(tax)
        context = {
            'grand_total': round((grand_total),2),
            'subtotal': subtotal,
            'tax_dict': tax_dict
        }
        return context
    
    def __str__(self):
        return self.order_number


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.fooditem.food_name