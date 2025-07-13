
from django.contrib import admin
from django.urls import path

from devis_app import views

urlpatterns = [
  path('', views.home, name= "index")
]
