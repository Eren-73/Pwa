from django.contrib import admin
from .models import Devis, LigneDevis, Produit, Categorie, Client
from django.utils.html import format_html


class LigneDevisInline(admin.TabularInline):
    model = LigneDevis
    extra = 1

from django.utils.html import format_html

class DevisAdmin(admin.ModelAdmin):
    inlines = [LigneDevisInline]
    list_display = ('numero_devis', 'date_emission', 'date_validite', 'total_ttc', 'qr_code_tag')
    search_fields = ('numero_devis',)
    list_filter = ('date_emission', 'date_validite')

    def qr_code_tag(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="50" height="50" />', obj.qr_code.url)
        return "-"
    qr_code_tag.short_description = 'QR Code'
    qr_code_tag.allow_tags = True

admin.site.register(Devis, DevisAdmin)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'categorie')  # champs affichés dans la liste
    search_fields = ('nom',)                      # barre de recherche sur le nom
    list_filter = ('categorie',)                  # filtres latéraux

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email')
    search_fields = ('prenom', 'nom', 'email')

# Enregistre les modèles avec leur admin personnalisé
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Client, ClientAdmin)