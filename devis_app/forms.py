from django import forms
from django.contrib.auth.models import User
from .models import Devis, LigneDevis, Client, Produit, Categorie, ResponsableCommercial


def get_responsables_choices():
    """Retourne les responsables commerciaux définis par l'admin."""
    choices = [('', '--- Sélectionner un responsable ---')]
    for r in ResponsableCommercial.objects.all():
        choices.append((r.nom, r.nom))
    return choices


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['client', 'point_vente', 'regime_vente', 'detail_proposition', 'date_proforma', 'date_validite', 'pourcentage_acompte', 'pourcentage_livraison', 'signature_electronique', 'nom_responsable']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'point_vente': forms.Select(attrs={'class': 'form-select'}),
            'regime_vente': forms.Select(attrs={'class': 'form-select'}),
            'detail_proposition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_proforma': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_validite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pourcentage_acompte': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'pourcentage_livraison': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'signature_electronique': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'nom_responsable': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Peuple le dropdown avec les utilisateurs actifs à chaque instanciation
        self.fields['nom_responsable'].widget.choices = get_responsables_choices()

class LigneDevisForm(forms.ModelForm):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = LigneDevis
        fields = ['produit', 'quantite', 'unite', 'remise']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produit'].queryset = Produit.objects.all().order_by('nom')
        self.fields['produit'].label_from_instance = (
            lambda obj: f"[{obj.code or 'SANS-CODE'}] {obj.nom} - Stock: {obj.stock} - {obj.prix} CFA"
        )


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["nom","prenom", "email", "telephone", "adresse"]  # 🔹 Ajout adresse


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['code', 'nom', 'prix', 'stock', 'categorie']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
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
    from .models import PointVente
    
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
    telephone = forms.CharField(
        required=False,
        label='Téléphone',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    point_vente = forms.ModelChoiceField(
        queryset=PointVente.objects.all(),
        required=False,
        label='Point de vente',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Actif',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'telephone', 'point_vente', 'is_active', 'password1', 'password2')

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
        profile.telephone = self.cleaned_data.get('telephone')
        profile.point_vente = self.cleaned_data.get('point_vente')
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