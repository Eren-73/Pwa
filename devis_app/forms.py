from django import forms
from .models import Devis, LigneDevis,Client,Produit,Categorie

class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['client', 'point_vente', 'regime_vente', 'detail_proposition', 'date_proforma', 'date_validite']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'point_vente': forms.Select(attrs={'class': 'form-control'}),
            'regime_vente': forms.Select(
                attrs={'class': 'form-control'},
                choices=Devis.REGIME_CHOICES
            ),
            'detail_proposition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_proforma': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_validite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'point_vente': forms.Select(attrs={'class': 'form-select'}),
            'regime_vente': forms.Select(attrs={'class': 'form-select'}),
            'detail_proposition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_proforma': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_validite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

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


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CommercialCreateForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Actif',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter la classe form-control aux champs par défaut de UserCreationForm
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        # profile will be created by signals.post_save; ensure role is set to commercial
        try:
            profile = user.profile
        except Exception:
            from .models import Profile
            profile = Profile.objects.create(user=user)
        profile.role = 'commercial'
        profile.save()
        return user


class PointVenteForm(forms.ModelForm):
    class Meta:
        from .models import PointVente
        model = PointVente
        fields = ['nom', 'adresse', 'telephone']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }