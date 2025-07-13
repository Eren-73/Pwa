
from django.contrib import admin
from .models import Client, Produit, Devis, LigneDevis

admin.site.register(Client)
admin.site.register(Produit)
admin.site.register(Devis)
admin.site.register(LigneDevis)
