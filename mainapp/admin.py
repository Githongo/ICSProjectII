from django.contrib import admin

from mainapp.models import ClassifiedTopic, ClassifiedTweet

# Register your models here.
admin.site.register(ClassifiedTopic)
admin.site.register(ClassifiedTweet)