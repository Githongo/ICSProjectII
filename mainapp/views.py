from django.shortcuts import render

from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from tensorflow.keras.preprocessing import text

from mainapp.apps import MainappConfig
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from sentimentanalyser.settings import BASE_DIR

import tweepy
import os
import re

import numpy as np
import pandas as pd
from tensorflow import keras 
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
 


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

        tweets = fetchTweets(topics)

        tweets_list = []
        for tweet in tweets:
            tweets_list.append([tweet[3]])

        #sample_tweets = [['Apple music is good #the best'], ['Iphone 13 is bad @terrible UI'], ['The weather before and after'], ['Week good at iphone https://www.geeksforgeeks.org/different-ways-to-create-pandas-dataframe/'], ['Good']]
        #tweets_df = pd.DataFrame(sample_tweets, columns = ['text'])

        tweets_df = pd.DataFrame(tweets_list, columns=['text'])

        path = os.path.join(BASE_DIR, 'mainapp/models/sentModel.h5')
        reconstructed_model = keras.models.load_model(path)

        preprocessed = preprocessor(tweets_df)
        prediction = reconstructed_model.predict(preprocessed)

        classes_x=np.argmax(prediction,axis=1)

        classes = [""]*len(classes_x)
        for i, sent in enumerate(classes_x):
            if(sent == 0):
                classes[i] = "Negative"
            elif(sent == 1):
                classes[i] = "Neutral"
            elif(sent == 2):
                classes[i] = "Positive" 


        for index, tweet in enumerate(tweets):
            tweet.insert(4, classes[index])

        classified_tweets = tweets
        context = {
            "title": "Analysed Tweets",
            "classified_tweets": classified_tweets,
        }
        return render(request, 'pages/analyse.html', context)

@login_required
def classify(request):
    if request.method == 'GET':
        context = {
            "title": "Classify",
        }
        return render(request, 'pages/classify.html', context)
    
    elif request.method == 'POST':
        text = request.POST['classifyText']
        textList = [text]
        text_df = pd.DataFrame(textList, columns=['text'])

        path = os.path.join(BASE_DIR, 'mainapp/models/sentModel.h5')
        reconstructed_model = keras.models.load_model(path)

        preprocessed = preprocessor(text_df)
        predicted = reconstructed_model.predict(preprocessed)
        
        classified =np.argmax(predicted,axis=1)
        print(classified[0])

        sentiment = "Not Analysed"
        if(classified[0] == 0):
            sentiment = "Negative"
        elif(classified[0] == 1):
            sentiment = "Neutral"
        elif(classified[0] == 2):
            sentiment = "Positive"

        context = {
            "text": sentiment,
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
    
    corona_tweets = tweepy.Cursor(api.search_tweets, q=topics+"-filter:retweets",lang = "en", show_user = True,tweet_mode="extended").items(50)
    corona_tweets_list = [[tweet.created_at, tweet.place, tweet.user.name, tweet.full_text] for tweet in corona_tweets]

    return corona_tweets_list #Tweet text at [0][3]


def preprocessor(tweets_df):
    #remove chars
    pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|#[a-zA-Z]+|$[a-zA-Z]+|@[a-zA-Z]+|[,.^_$*%-;鶯!?:]')
    for i in range(len(tweets_df["text"])):
        tweets_df["text"][i] = pattern.sub('', tweets_df["text"][i])

    # Text tokenization
    tokenizer = Tokenizer(num_words=500, lower=True, split=' ')
    tokenizer.fit_on_texts(tweets_df['text'])

    # Transforms text to a sequence of integers
    X = tokenizer.texts_to_sequences(tweets_df['text'])
    # Pad sequences to the same length
    X = pad_sequences(X, padding='post', maxlen=20)

    tweets_arr = X
    return tweets_arr