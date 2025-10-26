"""
URLs pour la gestion des points de vente.
"""
from django.urls import path
from devis_app import views

app_name = 'points_vente'

urlpatterns = [
    path('', views.liste_point_ventes, name='liste'),
    path('ajouter/', views.ajouter_point_vente, name='ajouter'),
    path('modifier/<int:pk>/', views.modifier_point_vente, name='modifier'),
    path('supprimer/<int:pk>/', views.supprimer_point_vente, name='supprimer'),
]