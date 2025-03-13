from django.urls import path
from .views import user_login, user_logout, register, home

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
]
