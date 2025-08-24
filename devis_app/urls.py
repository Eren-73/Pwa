from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('creer/', views.creer_devis, name='creer_devis'),
    path('facture/<int:pk>/', views.imprimer_devis, name='imprimer_devis'),
    path("clients/", views.liste_clients, name="liste_clients"),  # ✅ nouvelle route
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),



    ]
