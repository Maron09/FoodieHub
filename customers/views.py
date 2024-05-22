from django.shortcuts import render,redirect
from django.shortcuts import render, get_object_or_404
from accounts.views import *

# Create your views here.
@login_required(login_url='login')
# @user_passes_test(check_role_customer)
def customerProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile Updated')
            return redirect('c-profile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile
    }
    return render(request, 'customers/c_profile.html', context)