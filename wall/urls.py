from django.urls import path
from . import views

urlpatterns = [
    path('', views.wall_main, name='wall-main'),
    path('<str:kind>-view', views.wall_view, name='wall-view'),
    path('<str:kind>-view-page', views.wall_view_page, name='wall-view-page')
]