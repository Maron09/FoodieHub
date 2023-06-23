from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages





def registerUser(request):
    if request.method == 'POST':
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
