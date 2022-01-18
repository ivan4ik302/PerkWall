from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_main, name='payment-main'),
    path('webhook', views.payment_webhook, name='payment-webhook'),
]