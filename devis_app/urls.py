from django.urls import path,include 
from . import views
from . import views_theme  # Import pour theme toggle
from django.contrib.auth import views as auth_views  # 🔹 Import correct de Django

urlpatterns = [
    # ---- Theme Toggle (HTMX) ----
    path('api/theme/toggle/', views_theme.toggle_theme, name='toggle_theme'),
    path('api/theme/get/', views_theme.get_theme, name='get_theme'),
    
    path('', views.dashboard, name='dashboard'),
    path('creer/', views.creer_devis, name='creer_devis'),
    path('creer/<slug:slug>/', views.creer_devis, name='modifier_devis_v2'),  # Nouvelle route pour modification
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
    path("devis/<slug:slug>/modifier/", views.modifier_devis, name="modifier_devis"),
    path("devis/<slug:slug>/historique/", views.historique_devis, name="historique_devis"),
    path('historique/<int:historique_id>/voir/', views.voir_version_historique, name='voir_version_historique'),
    path("devis/<slug:slug>/export/pdf/", views.export_pdf, name="export_pdf"),
    path("devis/<slug:slug>/envoyer-email/", views.envoyer_devis_par_email, name="envoyer_devis_par_email"),

    # ---- Matériels & Produits ----
    path('materiels/', views.liste_materiels, name='liste_materiels'),
    path('produit/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produit/modifier/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('produit/supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),

    # ---- Catégories ----
    path('categorie/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),

    #---Authentification---#
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    #---Portail Client---#
    path('client/<slug:client_slug>/factures/', views.client_factures, name='client_factures'),

    #---API---#
    path('api/responsables/', views.responsables_suggestions, name='responsables_suggestions'),


    # Responsables Commerciaux
    path('responsables/', views.liste_responsables, name='liste_responsables'),
    path('responsables/ajouter/', views.ajouter_responsable, name='ajouter_responsable'),
    path('responsables/supprimer/<int:pk>/', views.supprimer_responsable, name='supprimer_responsable'),

    #---DASHBOARD---#
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('commerciaux/', views.commerciaux_devis_list, name='commerciaux_devis_list'),
    
    # Commerciaux CRUD
    path('commerciaux/liste/', views.liste_commerciaux, name='liste_commerciaux'),
    path('commerciaux/creer/', views.create_commercial, name='create_commercial'),
    path('commerciaux/modifier/<int:user_id>/', views.modifier_commercial, name='modifier_commercial'),
    path('commerciaux/supprimer/<int:user_id>/', views.supprimer_commercial, name='supprimer_commercial'),
    
    # QR Codes
    path('admin/regenerate-qr/', views.regenerate_qr_codes_view, name='regenerate_qr_codes'),
    
    # Points de vente CRUD
    path('points-vente/', views.liste_point_ventes, name='liste_point_ventes'),
    path('points-vente/ajouter/', views.ajouter_point_vente, name='ajouter_point_vente'),
    path('points-vente/modifier/<int:pk>/', views.modifier_point_vente, name='modifier_point_vente'),
    path('points-vente/supprimer/<int:pk>/', views.supprimer_point_vente, name='supprimer_point_vente'),
]

