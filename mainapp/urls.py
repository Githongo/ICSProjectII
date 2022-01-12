from os import name
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('analyse/', views.analyse, name='analyse'),
    path('classify/', views.classify, name='classify'),
    path('analysed/', views.analysed, name='analysed'),
    path('analysed/delete/(?P<id>\d+)/$', views.delete_analysed, name='analysed.delete'),
    path('classified/', views.classified, name='classified'),
    path('classified/delete/(?P<id>\d+)/$', views.delete_classified, name='classified.delete'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

]