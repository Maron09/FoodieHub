from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from vendor.models import *
from django.shortcuts import render, get_object_or_404
from menu.models import *
from django.db.models import Prefetch
from .models import *
from .context_processors import *
from django.contrib.auth.decorators import login_required




def marketPlace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request,'marketPlace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'products',
            queryset=Product.objects.filter(is_available=True)
        )
    ) # prefetch looks for the data in a reverse manner eg. if a model is not in maodel that has been called but want to get the item that is related to the model
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items
    }
    return render(request,'marketplace/vendor_detail.html', context)


def addToCart(request, food_id):
    
    if request.user.is_authenticated:
        if request.is_ajax():
            # check if food exists
            try:
                fooditem = Product.objects.get(id=food_id)
                # check if user has added the food to the cart
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditems=fooditem)
                    #increase cart quantity
                    checkCart.quantity += 1
                    checkCart.save()
                    return JsonResponse({'status': 'success', 'message': 'Cart increased', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    # creates one if it doesn't exist
                    checkCart = Cart.objects.create(user=request.user, fooditems=fooditem, quantity=1)
                    return JsonResponse({'status': 'success', 'message': 'Food added to Cart', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Login to Continue'})



def decreaseCart(request, food_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            # check if food exists
            try:
                fooditem = Product.objects.get(id=food_id)
                print(f'food_id: {food_id}')
                # check if user has added the food to the cart
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditems=fooditem)
                    if checkCart.quantity > 1:
                        #decrease cart quantity
                        checkCart.quantity -= 1
                        checkCart.save()
                    else:
                        checkCart.delete()
                        checkCart.quantity = 0
                    return JsonResponse({'status': 'success', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'Food not in Cart'})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Login to Continue'})

@login_required(login_url='login')
def cartPage(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def deleteItem(request, cart_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            try:
                #if item exist
                cart_item= Cart.objects.filter(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'success', 'message': 'Item Deleted', 'cart_counter': get_cart_counter(request),'cart_amount': get_cart_amount(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
        