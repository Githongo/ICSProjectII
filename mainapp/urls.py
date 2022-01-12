from os import name
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('analyse/', views.analyse, name='analyse'),
    path('classify/', views.classify, name='classify'),
    path('analysed/', views.analysed, name='analysed'),
    path('classifed/', views.classified, name='classified'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),



]