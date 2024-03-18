from django.urls import path
from .views import *
from .webhook import webhook

urlpatterns = [
    path('', base, name='base'),
    path('webhook/', webhook, name='webhook'),
]
