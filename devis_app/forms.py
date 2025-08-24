from django import forms
from .models import Devis, LigneDevis,Client

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
        fields = ["nom", "email", "telephone", "adresse"]  # 🔹 Ajout adresse
