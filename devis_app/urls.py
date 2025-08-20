from django.urls import path
from . import views

urlpatterns = [
    path('creer/', views.creer_devis, name='creer_devis'),
    path('facture/<int:pk>/', views.imprimer_devis, name='imprimer_devis'),
    ]
