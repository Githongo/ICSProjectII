from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    context = {
        "title" : "Login to Continue",
    }
    return render(request, 'account/login.html', context)

def home(request):
    context = {
        "title" : "Dashboard",
    }
    return render(request, 'pages/home.html', context)