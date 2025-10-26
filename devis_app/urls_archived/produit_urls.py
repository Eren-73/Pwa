"""
URLs pour la gestion des produits et catégories.
"""
from django.urls import path
from devis_app import views

app_name = 'produits'

urlpatterns = [
    path('', views.liste_materiels, name='liste'),
    path('ajouter/', views.ajouter_produit, name='ajouter'),
    path('modifier/<int:produit_id>/', views.modifier_produit, name='modifier'),
    path('supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer'),
    path('categorie/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
]