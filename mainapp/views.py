from django.shortcuts import redirect, render

from django.http.response import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from mainapp.models import ClassifiedTopic, ClassifiedTweet
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
    if request.user.is_authenticated:
        return HttpResponseRedirect("/home")
    else:
        context = {
            "title" : "Login to Continue",
        }
        return render(request, 'account/login.html', context)

@login_required
def home(request):
    positive_tweets_count = ClassifiedTopic.objects.filter(sentiment="Positive").count()
    neutral_tweets_count = ClassifiedTopic.objects.filter(sentiment="Neutral").count()
    negative_tweets_count = ClassifiedTopic.objects.filter(sentiment="Negative").count()

    context = {
        "title" : "Dashboard",
        "positive_tweets_count": positive_tweets_count,
        "neutral_tweets_count": neutral_tweets_count,
        "negative_tweets_count": negative_tweets_count,
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
        #getting topics from request
        topics = request.POST['topics']
        topics = topics.replace(" ", "")
        topics = topics.replace(",", " OR ")

        #fetching 50 tweets associated with the topics
        tweets = fetchTweets(topics)

        #making a list then a dataframe of the text from the fetched tweets
        tweets_list = []
        for tweet in tweets:
            tweets_list.append([tweet[3]])

        tweets_df = pd.DataFrame(tweets_list, columns=['text'])

        #loading saved model
        path = os.path.join(BASE_DIR, 'mainapp/models/sentModel.h5')
        reconstructed_model = keras.models.load_model(path)

        #doing some data preprocessing
        preprocessed = preprocessor(tweets_df)
        #model prediction
        prediction = reconstructed_model.predict(preprocessed)
        #getting classes from the predictions
        classes_x=np.argmax(prediction,axis=1)

        #Attaching corresponding sentiment strings to the classified classes
        classes = [""]*len(classes_x)
        for i, sent in enumerate(classes_x):
            if(sent == 0):
                classes[i] = "Negative"
            elif(sent == 1):
                classes[i] = "Neutral"
            elif(sent == 2):
                classes[i] = "Positive" 

        #Inserting the obtained sentiments to the initial fetched tweets
        for index, tweet in enumerate(tweets):
            tweet.insert(4, classes[index])
            #replacing null location values with 'not specified'
            location = "Not Specified"
            if (tweet[1] != None):
                location = tweet[1]
            #saving classified tweet to DB
            classifiedTopic = ClassifiedTopic(
                date=tweet[0],
                location=location,
                username=tweet[2],
                tweet=tweet[3],
                sentiment=tweet[4],
            )
            classifiedTopic.save()

        classified_tweets = tweets

        context = {
            "title": "Analysed Tweets",
            "classified_tweets": classified_tweets,
        }
        return render(request, 'pages/analyse.html', context)


@login_required
def delete_analysed(request, id):
    ClassifiedTopic.objects.get(id=id).delete()
    return redirect('/analysed')

@login_required
def delete_classified(request, id):
    ClassifiedTweet.objects.get(id=id).delete()
    return redirect('/classified')

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

        #loading model
        path = os.path.join(BASE_DIR, 'mainapp/models/sentModel.h5')
        reconstructed_model = keras.models.load_model(path)
        #Text preprocessing and sentiment prediction
        preprocessed = preprocessor(text_df)
        predicted = reconstructed_model.predict(preprocessed)
        #obtaining sentiment class
        classified =np.argmax(predicted,axis=1)
        print(classified[0])

        #Attaching corresponding sentiment string to class value
        sentiment = "Not Analysed"
        if(classified[0] == 0):
            sentiment = "Negative"
        elif(classified[0] == 1):
            sentiment = "Neutral"
        elif(classified[0] == 2):
            sentiment = "Positive"

        #Saving classified tweet to DB
        classifiedTweet = ClassifiedTweet(
            username = request.user,
            tweet = text,
            sentiment = sentiment,
        )
        classifiedTweet.save()

        context = {
            "text": sentiment,
        }
        return render(request, 'pages/classify.html', context)

@login_required
def analysed(request):
    if request.method == 'GET':

        analysed_tweets = ClassifiedTopic.objects.all()
        context = {
            "title": "Analysed Tweet topics",
            "analysed_tweets": analysed_tweets, 
        }
        return render(request, 'pages/analysed.html', context)
    
@login_required
def classified(request):
    classified_tweets = ClassifiedTweet.objects.all()
    if request.method == 'GET':
        context = {
            "title": "Classified Tweets",
            "classified_tweets": classified_tweets,
        }
        return render(request, 'pages/classified.html', context)


def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect("/home")
        else:
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

    return corona_tweets_list


def preprocessor(tweets_df):
    #remove unwated chars, links, etc.
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