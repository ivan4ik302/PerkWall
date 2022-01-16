from django.urls import path
from . import views

urlpatterns = [
    path('login', views.account_login, name='account-login'),
    path('registration', views.account_registration, name='account-registration'),
    path('logout', views.account_logout, name='account-logout')
]