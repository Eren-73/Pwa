from django.contrib import admin
from .models import Devis, LigneDevis, Produit, Categorie, Client, ActionCommercial, Profile, PointVente
from django.utils.html import format_html
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


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
        return obj.user.devis.count()  
    nombre_devis.short_description = "Nombre de devis"


# 🔹 Admin pour le modèle Profile (Commerciaux)
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('role', 'point_vente', 'telephone')


# 🔹 Admin étendu pour User avec Profile intégré
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_point_vente', 'get_telephone', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except:
            return "-"
    get_role.short_description = 'Rôle'
    
    def get_point_vente(self, obj):
        try:
            return obj.profile.point_vente.nom if obj.profile.point_vente else "-"
        except:
            return "-"
    get_point_vente.short_description = 'Point de vente'
    
    def get_telephone(self, obj):
        try:
            return obj.profile.telephone if obj.profile.telephone else "-"
        except:
            return "-"
    get_telephone.short_description = 'Téléphone'


# 🔹 Admin pour PointVente
class PointVenteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'telephone', 'nombre_commerciaux')
    search_fields = ('nom', 'adresse', 'telephone')
    
    def nombre_commerciaux(self, obj):
        return obj.profile_set.count()
    nombre_commerciaux.short_description = 'Nombre de commerciaux'


# 🔹 Désenregistrer le User par défaut et enregistrer notre version personnalisée
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 🔹 Enregistre les modèles avec leur admin personnalisé
admin.site.register(Devis, DevisAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ActionCommercial, ActionCommercialAdmin)
admin.site.register(PointVente, PointVenteAdmin)
