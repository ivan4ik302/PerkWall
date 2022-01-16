from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_main, name='dashboard-main'),
    path('account', views.dashboard_account, name='dashboard-account'),
    path('user-subscription', views.dashboard_user_subscription, name='dashboard-user-subscription'),
    path('user-product', views.dashboard_user_product, name='dashboard-user-product'),
    path('user-subscription-product', views.dashboard_user_subscription_product, name='dashboard-user-subscription-product'),
    path('user-<str:kind>-preview', views.dashboard_user_preview, name='dashboard-user-preview'),
    path('user-<str:kind>-view-page', views.dashboard_user_view_page, name='dashboard-user-view-page'),
    path('<str:kind>-view-page', views.dashboard_view_page, name='dashboard-view-page')
]