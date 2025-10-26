"""
URLs pour la gestion des clients.
"""
from django.urls import path
from devis_app import views

app_name = 'clients'

urlpatterns = [
    path('', views.liste_clients, name='liste'),
    path('ajouter/', views.ajouter_client, name='ajouter'),
    path('modifier/<slug:slug>/', views.modifier_client, name='modifier'),
    path('supprimer/<slug:slug>/', views.supprimer_client, name='supprimer'),
    path('<slug:slug>/devis/', views.devis_par_client, name='devis'),
]