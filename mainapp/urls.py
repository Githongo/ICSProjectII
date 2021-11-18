from os import name
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('classify/', views.classify, name='classify'),
    path('result/', views.result, name='result'),


]