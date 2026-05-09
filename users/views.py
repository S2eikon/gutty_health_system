from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


# REGISTRO

def register_view(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            
            role = request.POST.get('role')

            if role in ['patient', 'doctor']:
                user.role = role
            else:
                user.role = 'patient'

            user.save()
            login(request, user)

            return redirect('/appointments/')

    return render(request, 'users/register.html', {'form': form})



# LOGIN

def login_view(request):
    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('/appointments/')

    return render(request, 'users/login.html', {'form': form})



# LOGOUT

def logout_view(request):
    logout(request)
    return redirect('/users/login/')