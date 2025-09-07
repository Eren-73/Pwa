from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('creer/', views.creer_devis, name='creer_devis'),
    path('facture/<slug:slug>/', views.devis_template , name='devis_template'),

    # ---- Clients ----
    path("clients/", views.liste_clients, name="liste_clients"),
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    path('clients/<slug:slug>/modifier/', views.modifier_client, name='modifier_client'),
    path('clients/<slug:slug>/supprimer/', views.supprimer_client, name='supprimer_client'),
    path('clients/<slug:slug>/devis/', views.devis_par_client, name='devis_par_client'),

    # ---- Devis ----
    path("devis/supprimer-selection/", views.supprimer_devis_selectionnes, name="supprimer_devis_selectionnes"),  # ⚠️ placé avant <slug>
    path("devis/<slug:slug>/", views.detail_devis, name="detail_devis"),

    # ---- Matériels & Produits ----
    path('materiels/', views.liste_materiels, name='liste_materiels'),
    path('produit/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produit/modifier/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('produit/supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),

    # ---- Catégories ----
    path('categorie/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),

     # ---- Import ----
    # path('devis/<slug:slug>/export/pdf/', views.export_devis_pdf, name='export_devis_pdf'),
    # path('devis/<slug:slug>/export/word/', views.export_devis_word, name='export_devis_word'),
    # path('devis/<slug:slug>/export/excel/', views.export_devis_excel, name='export_devis_excel'),

]
