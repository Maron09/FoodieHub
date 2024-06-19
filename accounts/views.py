from django.shortcuts import render,redirect

from orders.models import Order
from .forms import *
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test # activates custom decorators
from vendor.forms import *
from .models import *
from .utils import *
from django.core.exceptions import PermissionDenied
from vendor.models import *
from django.template.defaultfilters import slugify

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
        return redirect('my-account')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password'] #Hashing the password 
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            
            #Send verification email
            mail_subject = 'Activate your Account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            
            messages.success(request, 'Registration Successful--check email for verification! ')
            return redirect('register-user')
        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Already logged in')
        return redirect('my-account')
    elif request.method == 'POST':
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
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id) # makes it unique
            user_profile =  UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            #Send verification email
            mail_subject = 'Activate your Account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            
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


def activate(request, uidb64, token):
    #Activate the user account to set the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account Activated successfully')
        return redirect('my-account')
    else:
        messages.error(request, 'Invalid Link')
        return redirect('my-account')


def loginPage(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Already logged in')
        return redirect('my-account')
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
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    order_count = orders.count()
    context = {
        'orders': orders,
        'order_count': order_count,
        'recent_orders': recent_orders
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user= request.user)
    context = {
        'vendor': vendor
    }
    return render(request, 'accounts/vendor_dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            
            #send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            
            messages.info(request, 'Link to reset password sent! Check Email')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot-password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Reset your Password')
        return redirect('reset-password')
    else:
        messages.error(request, 'Link is Expired')
        return redirect('my-account')



def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password changed Successfully')
            return redirect('login')
        else:
            messages.error(request, 'Password do not Match!')
            return redirect('reset-password')
    return render(request, 'accounts/reset_password.html')