from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test # activates custom decorators
from vendor.forms import *
from .models import *
from .utils import *
from django.core.exceptions import PermissionDenied

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Already logged in')
        return redirect('dashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password'] #Hashing the password 
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Registration Successful')
            return redirect('register-user')
        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def registerVendor(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES) # request.FILES receives files 
        if form.is_valid() and v_form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.VENDOR
            user.save()  
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile =  UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Registration Successful - Wait for Approval.')
            return redirect('register-vendor')
        else: 
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form':form,
        'v_form':v_form,
    }
    return render(request, 'accounts/register_vendor.html', context)



def loginPage(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Already logged in')
        return redirect('dashboard')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Returns which user owns the email and password
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)   
            messages.success(request, 'Login Successful')
            return redirect('my-account')
        else:
            messages.error(request, 'Invalid Input')
            return redirect('login')
    return render(request, 'accounts/login.html')


def logoutPage(request):
    auth.logout(request)
    messages.info(request, 'Logged out')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request, 'accounts/customer_dashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendor_dashboard.html')