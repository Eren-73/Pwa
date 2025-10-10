from django.contrib import admin
from .models import Devis, LigneDevis, Produit, Categorie, Client,ActionCommercial
from django.utils.html import format_html
from django.db.models import Count


# 🔹 Inline pour afficher les lignes de devis directement dans l'admin Devis
class LigneDevisInline(admin.TabularInline):
    model = LigneDevis
    extra = 1

# 🔹 Admin pour le modèle Devis
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

# 🔹 Admin pour le modèle Produit
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'categorie')  # champs affichés dans la liste
    search_fields = ('nom',)                      # barre de recherche sur le nom
    list_filter = ('categorie',)                  # filtres latéraux

# 🔹 Admin pour le modèle Categorie
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

# 🔹 Admin pour le modèle Client
class ClientAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email')
    search_fields = ('prenom', 'nom', 'email')
class ActionCommercialAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'date_action', 'ip_address', 'nombre_devis')
    list_filter = ('user', 'date_action')
    ordering = ('-date_action',)

    def nombre_devis(self, obj):
        # Compte le nombre total de devis créés par cet utilisateur
        return obj.user.devis_utilisateur.count()  
    nombre_devis.short_description = "Nombre de devis"


# 🔹 Enregistre les modèles avec leur admin personnalisé
admin.site.register(Devis, DevisAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ActionCommercial, ActionCommercialAdmin)
