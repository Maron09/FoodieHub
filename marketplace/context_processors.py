from .models import *
from menu.models import *
from decimal import Decimal

def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amount(request):
    subtotal = Decimal('0.00')
    tax = Decimal('0.00')
    grand_total = Decimal('0.00')
    tax_dict = {}
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = Product.objects.get(id=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity)
        
        # getting the tax from the database and calculating it
        get_tax = Tax.objects.filter(is_active=True)
        for tax_item in get_tax:
            tax_type = tax_item.tax_type
            tax_percentage = tax_item.tax_percentage
            tax_amount = round((tax_percentage * subtotal) / 100, 2)
            
            # creating a nested dictionary
            tax_dict.update({tax_type: {tax_percentage: float(tax_amount)}})
        
        tax = sum(float(x) for key in tax_dict.values() for x in key.values())
        grand_total = float(subtotal) + float(tax)
        
    return dict(subtotal=float(subtotal), tax=float(tax), grand_total=float(grand_total), tax_dict=tax_dict)