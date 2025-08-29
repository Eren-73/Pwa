from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('creer/', views.creer_devis, name='creer_devis'),
    path('facture/<int:pk>/', views.devis_template , name='devis_template '),
    path("clients/", views.liste_clients, name="liste_clients"),  # ✅ nouvelle route
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    path('clients/<int:pk>/modifier/', views.modifier_client, name='modifier_client'),
    path('clients/<int:pk>/supprimer/', views.supprimer_client, name='supprimer_client'),
    path('clients/<int:pk>/devis/', views.devis_par_client, name='devis_par_client'),
    path("devis/<int:devis_id>/", views.detail_devis, name="detail_devis"),




    ]
