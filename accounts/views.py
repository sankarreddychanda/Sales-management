from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def home(request):
    return render(request, 'home.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'sales':
                return redirect('sales_dashboard')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import CustomUser  # Import your CustomUser model

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            # Create the user using CustomUser
            user = CustomUser.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Log the user in
            login(request, user)

            # Redirect to the appropriate dashboard based on role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'sales':
                return redirect('sales_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'register.html')
