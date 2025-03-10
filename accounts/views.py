from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


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
                messages.error(request, "Invalid user role")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request, 'home.html')
