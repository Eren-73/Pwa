"""
URLs pour la gestion des commerciaux.
"""
from django.urls import path
from devis_app import views

app_name = 'commerciaux'

urlpatterns = [
    path('liste/', views.commerciaux_devis_list, name='liste'),
    path('creer/', views.create_commercial, name='creer'),
]