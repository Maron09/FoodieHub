from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from orders.models import OrderedFood
from .forms import *
from accounts.forms import *
from .models import *
from accounts.models import *
from django.contrib import messages
from accounts.views import *
from menu.models import *
from .utils import *
from menu.forms import *
from django.template.defaultfilters import slugify



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.info(request, "Upadate successful ")
            return redirect('v-profile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile':profile,
        'vendor':vendor,
    }
    return render(request, 'vendor/v_profile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorMenuBuilder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def foodItem_by_cat(request, pk):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditem = Product.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditem':fooditem,
        "category":category
    }
    return render(request, 'vendor/food_item.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def addCategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category added successfully')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def editCategory(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category':category
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def deleteCategory(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted Succesfully')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def addFood(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            food_name = form.cleaned_data['food_name']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_name)
            form.save()
            messages.success(request, 'Food added successfully')
            return redirect('fooditem_by_cat', food.category.id)
        else:
            print(form.errors)
    else:
        form = ProductForm()
        #Modify the form query
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def editFood(request, pk=None):
    food = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_name = form.cleaned_data['food_name']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_name)
            form.save()
            messages.success(request, 'Food updated successfully')
            return redirect('fooditem_by_cat', food.category.id)
        else:
            print(form.errors)
    else:
        form = ProductForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food':food
    }
    return render(request,'vendor/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def deleteFood(request, pk=None):
    food = get_object_or_404(Product, pk=pk)
    food.delete()
    messages.success(request, 'Food deleted Succesfully')
    return redirect('fooditem_by_cat', food.category.id)



def opening_hour(request):
    opening_hours = Opening_hour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours
    }
    return render(request,'vendor/open_hours.html', context)


def addOpenHours(request):
    # handle the data and save to the database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            try:
                hour = Opening_hour.objects.create(vendor=get_vendor(request),day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = Opening_hour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day':  day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour+'-'+to_hour+ ' already exists for this day!'}
                return JsonResponse(response)
        else:
            HttpResponse('Invalid request')


def removeOpenHours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(Opening_hour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))
        subtotal = order.get_total_by_vendor()['subtotal']
        tax = order.get_total_by_vendor()['tax_dict']
        grand_total = order.get_total_by_vendor()['grand_total']
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax,
            'grand_total': grand_total,
        }
        return render(request, 'vendor/vendor_order_detail.html', context)
    except:
        return redirect('vendor')



def my_orders(request):
    vendor = Vendor.objects.get(user= request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'vendor/my_orders.html', context)