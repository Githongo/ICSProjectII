from django.shortcuts import render

from django.http import HttpResponse
from django.http.response import HttpResponseRedirect

from mainapp.apps import MainappConfig
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

import tweepy


def index(request):
    
    context = {
        "title" : "Login to Continue",
    }
    return render(request, 'account/login.html', context)

@login_required
def home(request):
    context = {
        "title" : "Dashboard",
    }
    return render(request, 'pages/home.html', context)

@login_required
def analyse(request):

    if request.method == 'GET':
        context = {
            "title": "Analyse Tweets",
        }
        return render(request, 'pages/analyse.html', context)
    elif request.method == 'POST':
        topics = request.POST['topics']
        topics = topics.replace(" ", "")
        topics = topics.replace(",", " OR ")

        tweets = fetchTweets('a')

        context = {
            "title": "Analysed Tweets",
            "content": tweets,
        }
        return render(request, 'pages/analyse.html', context)

@login_required
def classify(request):
    context = {
        "title": "Classify",
    }
    return render(request, 'pages/classify.html', context)

@login_required
def result(request):
    text = request.GET['classifyText']
    #vectorized text
    vector = MainappConfig.vectorizer.transform([text])
    prediction = MainappConfig.model.predict(vector)[0]
    context = {
        "text": prediction,
    }
    return render(request, 'pages/classify.html', context)

def login(request):
    if request.method == 'GET':
        context = {
            "title" : "Login",
        }
        return render(request, 'account/login.html', context)

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect('/home')
        else:
            context = {
                "title" : "Login",
                "error": "Incorrect username or password",
            }
            return render(request, 'account/login.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def fetchTweets(topics):
    twitter_auth_keys = {
        "consumer_key": "mHz1VOi1NT34C6TPDlgCrJVQh",
        "consumer_secret": "3KTJrd68bwPsx0lvEfWlV5sKC41UJj16tWn4aUjFcIeKvHqjP2",
        "access_token": "998973769694810113-LYxfLnmSfv2RIDGxOwDp0DKI7ocruVX",
        "access_token_secret": "cI3AZTXJHGwWDkVKwfNGqMs50qjDyNbsbsD9bdfLRHkXG"
    }

    auth = tweepy.OAuthHandler(
        twitter_auth_keys['consumer_key'],
        twitter_auth_keys['consumer_secret']
    )
    auth.set_access_token(
        twitter_auth_keys['access_token'],
        twitter_auth_keys['access_token_secret']
    )
    api = tweepy.API(auth)
    
    corona_tweets = tweepy.Cursor(api.search_tweets, q="iPhone OR iOS OR Apple -filter:retweets",lang = "en", show_user = True,tweet_mode="extended").items(50)
    corona_tweets_list = [[tweet.created_at, tweet.place, tweet.user.name, tweet.full_text] for tweet in corona_tweets]
    

    return corona_tweets_list[0] #Tweet text at [3]
