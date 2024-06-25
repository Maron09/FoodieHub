from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from marketplace.models import *
from marketplace.context_processors import *
from .models import Order
from .forms import *
from .utils import *
import simplejson as json
from django.contrib.auth.decorators import login_required




@login_required(login_url='login')
def PlaceOrder(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    # if 0 no need to get to the checkout page
    if cart_count <= 0:
        return redirect('marketplace')
    
    vendor_ids = list({i.fooditem.vendor.id for i in cart_items})
    # print(vendor_ids)
    
    # calculating the subtotal for each vendor
    # vendor_subtotal = 0
    # k = {}
    # fooditem = [Product.objects.get(pk=i.fooditem.id, vendor_id__in=vendor_ids) for i in cart_items]
    # for i, j in zip(cart_items, fooditem):
    #     v_id = j.vendor.id
    #     if v_id in k:
    #         vendor_subtotal = k[v_id]
    #         vendor_subtotal += j.price * i.quantity
    #         k[v_id] = vendor_subtotal
    #     else:
    #         vendor_subtotal = j.price * i.quantity
    #         k[v_id] = vendor_subtotal
            
    # print(k)
    get_tax = Tax.objects.filter(is_active=True)
    total_data = {}
    vendor_subtotals = {}
    fooditems = [Product.objects.get(pk=i.fooditem.id, vendor_id__in=vendor_ids) for i in cart_items]

    # Calculate vendor subtotals
    for i, j in zip(cart_items, fooditems):
        v_id = j.vendor.id
        if v_id in vendor_subtotals:
            vendor_subtotals[v_id] += j.price * i.quantity
        else:
            vendor_subtotals[v_id] = j.price * i.quantity

    # Calculate tax data and construct total data
    for v_id, sub in vendor_subtotals.items():
        tax_dict = {}
        for tax in get_tax:
            tax_type = tax.tax_type
            tax_percentage = tax.tax_percentage
            tax_amount = round((tax_percentage * sub) / 100, 2)
            tax_dict[tax_type] = {str(tax_percentage): str(tax_amount)}
        
        total_data[v_id] = {str(sub): str(tax_dict)}

# Print the total data
    # print(total_data)

    
    # calculating the subtotal for each vendor using list comprehension and dictionary comprehension
    # vendor_subtotals = {}
    # fooditems = [Product.objects.get(pk=i.fooditem.id, vendor_id__in=vendor_ids) for i in cart_items]
    # for i, j in zip(cart_items, fooditems):
    #     v_id = j.vendor.id
    #     if v_id in vendor_subtotals:
    #         vendor_subtotals[v_id] += j.price * i.quantity
    #     else:
    #         vendor_subtotals[v_id] = j.price * i.quantity

    # for v_id, sub in vendor_subtotals.items():
    #     print(f'Vendor {v_id} Subtotal: {sub}')
    
    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']
    
    if request.method == 'POST':
        form = orderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.total_data = json.dumps(total_data)
            order.payment_method = request.POST['payment-method']
            # order id cannot be created unless the save function is called 
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendor_ids) #add the vendors for each order
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
def Payments(request):
    # Check if the request ia ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payement information in the payment model
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()
    
    
        # update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()
        
    
        # move he cart items to the orderfood model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity #total amount
            ordered_food.save()
            
        # send order confirmation email to the customer 
        mail_subject = "Thanks for Ordering"
        mail_template = 'orders/order_confirmation_email.html'
        ordered_food = OrderedFood.objects.filter(order=order)
        current_site = get_current_site(request)
        customer_subtotal = 0
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'user' : request.user,
            'order' : order,
            'ordered_food': ordered_food,
            'to_email' : order.email, # billing email address it might not be the login user email address
            'domain' : current_site,
            'customer_subtotal': customer_subtotal,
            'tax_data' : tax_data,
        }
        send_notification(mail_subject, mail_template, context)
        
        # send the order received email to the vendor
        mail_subject = "You have received an order"
        mail_template = 'orders/new_order_email.html'
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
                
                ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.fooditem.vendor)
                
                print(ordered_food_to_vendor)
                context = {
                    'order' : order,
                    'to_email' : i.fooditem.vendor.user.email,
                    'ordered_food_to_vendor': ordered_food_to_vendor,
                    'vendor_subtotal': get_vendor_total(order, i.fooditem.vendor.id)['subtotal'],
                    'tax_data': get_vendor_total(order, i.fooditem.vendor.id)['tax_dict'],
                    'vendor_total': get_vendor_total(order, i.fooditem.vendor.id)['grand_total'],
                }
                send_notification(mail_subject, mail_template, context)
        
        # clear the cart if the payment is successful
        cart_items.delete()
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
        # return back to ajax with the status success or failed
    return HttpResponse('Payment view')


def OrderComplete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    
    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        # getting the total from here rather than from cart 
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        
        tax_data = json.loads(order.tax_data)
        total = order.total
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
            'total': total
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')