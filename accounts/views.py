from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.contrib import messages
from django.views.decorators.cache import never_cache


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':

     if not request.POST.get('agree'):
        messages.error(request, "Please accept Terms & Conditions")
        return redirect('register')

    form = UserRegistrationForm(request.POST)

    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Account created successfully for {user.username}!")
        return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')


def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')