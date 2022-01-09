from django.db import models

# Create your models here.
class ClassifiedTopic(models.Model):
    date = models.CharField(max_length=200)
    location = models.CharField(max_length=1000)
    username = models.CharField(max_length=100)
    tweet = models.CharField(max_length=300)
    sentiment = models.CharField(max_length=50)

class ClassifiedTweet(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=100)
    tweet = models.CharField(max_length=500)
    sentiment = models.CharField(max_length=50)
