from django.apps import AppConfig
from django.conf import settings
import os
import pickle

from sentimentanalyser.settings import BASE_DIR

class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    path = os.path.join(BASE_DIR, 'mainapp/models/models.p')
    #load models into separate variables
    with open(path, 'rb') as pickled:
        data = pickle.load(pickled)
    model = data['model']
    vectorizer = data['vectorizer']
 
