from django import forms
from .models import Devis, LigneDevis,Client,Produit,Categorie

class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['client', 'regime_vente', 'detail_proposition', 'date_proforma', 'date_validite']

class LigneDevisForm(forms.ModelForm):
    class Meta:
        model = LigneDevis
        fields = ['produit', 'quantite', 'unite', 'remise']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["nom","prenom", "email", "telephone", "adresse"]  # 🔹 Ajout adresse


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'prix', 'categorie']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
        }

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }