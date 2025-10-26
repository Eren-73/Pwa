# Organisation des URLs

## Structure des URLs par Module

### 1. Devis (`urls/devis_urls.py`)
```python
urlpatterns = [
    path('creer/', views.creer_devis, name='creer'),
    path('<slug:slug>/', views.devis_template, name='template'),
    path('detail/<slug:slug>/', views.detail_devis, name='detail'),
    path('export-pdf/<slug:slug>/', views.export_pdf, name='export_pdf'),
    path('export-excel/<slug:slug>/', views.export_devis_excel, name='export_excel'),
    path('export-word/<slug:slug>/', views.export_devis_word, name='export_word'),
]
```

### 2. Clients (`urls/client_urls.py`)
```python
urlpatterns = [
    path('', views.liste_clients, name='liste'),
    path('ajouter/', views.ajouter_client, name='ajouter'),
    path('modifier/<slug:slug>/', views.modifier_client, name='modifier'),
    path('supprimer/<slug:slug>/', views.supprimer_client, name='supprimer'),
    path('<slug:slug>/devis/', views.devis_par_client, name='devis'),
]
```

### 3. Produits (`urls/produit_urls.py`)
```python
urlpatterns = [
    path('', views.liste_materiels, name='liste'),
    path('ajouter/', views.ajouter_produit, name='ajouter'),
    path('modifier/<int:produit_id>/', views.modifier_produit, name='modifier'),
    path('supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer'),
]
```

### 4. Points de Vente (`urls/point_vente_urls.py`)
```python
urlpatterns = [
    path('', views.liste_point_ventes, name='liste'),
    path('ajouter/', views.ajouter_point_vente, name='ajouter'),
    path('modifier/<int:pk>/', views.modifier_point_vente, name='modifier'),
    path('supprimer/<int:pk>/', views.supprimer_point_vente, name='supprimer'),
]
```

### 5. Commercial (`urls/commercial_urls.py`)
```python
urlpatterns = [
    path('liste/', views.commerciaux_devis_list, name='liste'),
    path('creer/', views.create_commercial, name='creer'),
]
```

## URL Principale (`urls.py`)
```python
urlpatterns = [
    path('devis/', include('devis_app.urls.devis_urls')),
    path('clients/', include('devis_app.urls.client_urls')),
    path('produits/', include('devis_app.urls.produit_urls')),
    path('points-vente/', include('devis_app.urls.point_vente_urls')),
    path('commerciaux/', include('devis_app.urls.commercial_urls')),
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
```

## Notes sur l'Organisation
- Chaque module a son propre fichier d'URLs
- Nommage cohérent des URLs et des vues
- Utilisation de slugs pour les identifiants lisibles
- Séparation claire des fonctionnalités