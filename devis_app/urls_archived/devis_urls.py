"""
URLs pour la gestion des devis.
"""
from django.urls import path
from devis_app import views

app_name = 'devis'

urlpatterns = [
    path('creer/', views.creer_devis, name='creer'),
    path('<slug:slug>/', views.devis_template, name='template'),
    path('detail/<slug:slug>/', views.detail_devis, name='detail'),
    path('export-pdf/<slug:slug>/', views.export_pdf, name='export_pdf'),
    path('export-excel/<slug:slug>/', views.export_devis_excel, name='export_excel'),
    path('export-word/<slug:slug>/', views.export_devis_word, name='export_word'),
    path('supprimer-selection/', views.supprimer_devis_selectionnes, name='supprimer_selection'),
]