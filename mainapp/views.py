from django.shortcuts import render

from django.http import HttpResponse

from mainapp.apps import MainappConfig


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

def classify(request):
    context = {
        "title": "Classify",
    }
    return render(request, 'pages/classify.html', context)

def result(request):
    text = request.GET['classifyText']
    #vectorized text
    vector = MainappConfig.vectorizer.transform([text])
    prediction = MainappConfig.model.predict(vector)[0]
    context = {
        "text": prediction,
    }
    return render(request, 'pages/classify.html', context)
