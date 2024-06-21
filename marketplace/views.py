from datetime import date, datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from orders.forms import orderForm
from vendor.models import *
from django.shortcuts import render, get_object_or_404
from menu.models import *
from django.db.models import Prefetch
from .models import *
from .context_processors import *
from .middlewares import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance #this assists in getting the restaurants near you




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
    ) # prefetch looks for the data in a reverse manner eg. if a model is not in model that has been called but want to get the item that is related to the model
    
    opening_hours = Opening_hour.objects.filter(vendor=vendor).order_by('day', '-from_hour')
    
    # Check current day's opening hours
    today_date = date.today()
    today = today_date.isoweekday() # this returns the numerical value of the day of the week just like in the model
    
    current_opening_hours = Opening_hour.objects.filter(vendor=vendor, day=today)
    
    
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
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
                    checkCart = Cart.objects.filter(user=request.user, fooditem=fooditem).first()
                    if checkCart:
                        # increase cart quantity
                        checkCart.quantity += 1
                        checkCart.save()
                    else:
                        # creates one if it doesn't exist
                        checkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)

                    cart_amount = get_cart_amount(request)
                    cart_amount = {k: float(v) if isinstance(v, Decimal) else v for k, v in cart_amount.items()}

                    return JsonResponse({
                        'status': 'success', 
                        'message': 'Cart increased', 
                        'cart_counter': get_cart_counter(request), 
                        'qty': checkCart.quantity, 
                        'cart_amount': cart_amount
                    })
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'Could not add food to cart'})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Login to Continue'})



def decreaseCart(request, food_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            try:
                fooditem = Product.objects.get(id=food_id)
                checkCart = Cart.objects.filter(user=request.user, fooditem=fooditem).first()
                if checkCart:
                    if checkCart.quantity > 1:
                        checkCart.quantity -= 1
                        checkCart.save()
                    else:
                        checkCart.delete()
                    cart_counter = get_cart_counter(request)
                    cart_amount = get_cart_amount(request)
                    return JsonResponse({
                        'status': 'success', 
                        'cart_counter': cart_counter, 
                        'qty': checkCart.quantity if checkCart else 0, 
                        'cart_amount': cart_amount
                    })
                return JsonResponse({'status': 'Failed', 'message': 'Food not in cart'})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Food does not exist'})
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
                cart_item = Cart.objects.filter(user=request.user, id=cart_id).first()
                if cart_item:
                    cart_item.delete()
                    cart_counter = get_cart_counter(request)
                    cart_amount = get_cart_amount(request)
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'Item deleted', 
                        'cart_counter': cart_counter, 
                        'cart_amount': cart_amount
                    })
                return JsonResponse({'status': 'Failed', 'message': 'Item does not exist'})
            except Exception as e:
                return JsonResponse({'status': 'Failed', 'message': str(e)})
        return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Login to Continue'})


def searchPage(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        lat = request.GET['lat']
        lng = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']
        
        # Get vendor ids that has the food item the user is looking for
        fetch_vendor_by_fooditems = Product.objects.filter(food_name__icontains=keyword, is_available=True).values_list('vendor', flat=True) #this gets the lost of vendors(ids) that have the food item the user is looking for
        
        
        
        # Q object is used for fetching complex search queries (this or that)
        vendors = Vendor.objects.filter(
            Q(id__in=fetch_vendor_by_fooditems ) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
        )
        
        
        if lat and lng and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (lng, lat))
            
            vendors = Vendor.objects.filter(
                Q(id__in=fetch_vendor_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                user_profile__locations__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__locations", pnt)).order_by("distance")
            
            # to get the distance between the user's location and the vendor
            for v in vendors:
                v.kms = round(v.distance.km, 1)

        vendor_count = vendors.count()
        context ={
            "vendors": vendors,
            "vendor_count": vendor_count,
            'source_location': address
        }
        
        
        return render(request,'marketplace/listings.html', context)

@login_required(login_url='login')
def CheckoutPage(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    # if 0 no need to get to the checkout page
    if cart_count <= 0:
        return redirect('marketplace')
    
    # Prepopulating the checkout page
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = orderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items
    }
    return render(request, 'marketplace/checkout.html', context)