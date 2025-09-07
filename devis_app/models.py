from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from datetime import timedelta
import uuid

from .utils import  generate_qr_code,nombre_en_lettres
from decimal import Decimal,ROUND_HALF_UP
from django.utils.crypto import get_random_string


class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nom


class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Générer un slug si vide
        if not self.slug:
            base_slug = slugify(f"{self.prenom} {self.nom}")
            slug_unique = base_slug
            counter = 1

            # Vérifier si le slug existe déjà
            while Client.objects.filter(slug=slug_unique).exists():
                slug_unique = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug_unique

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


def generate_numero_devis():
    return str(uuid.uuid4()).upper()[:19].replace('-', '-')


def default_date_validite():
    return now().date() + timedelta(days=30)



from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from decimal import Decimal, ROUND_HALF_UP

class Devis(models.Model):
    numero_devis = models.CharField(max_length=20, unique=True, blank=True)
    date_emission = models.DateField(default=now)
    date_validite = models.DateField(default=default_date_validite)
    date_proforma = models.DateField(default=now)
    regime_vente = models.CharField(max_length=10, default="TTC")
    detail_proposition = models.TextField(default='', null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    total_ht = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ht_remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ttc_lettres = models.CharField(max_length=255, blank=True, default='')

    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True, related_name="devis")

    def save(self, *args, **kwargs):
        # Générer un numéro unique si vide
        if not self.numero_devis:
            base = "DEVIS"
            unique_num = f"{base}-{get_random_string(6)}"
            while Devis.objects.filter(numero_devis=unique_num).exists():
                unique_num = f"{base}-{get_random_string(6)}"
            self.numero_devis = unique_num

        # Générer un slug si vide
        if not self.slug:
            self.slug = slugify(self.numero_devis)

        super().save(*args, **kwargs)  # 1ère sauvegarde pour avoir un PK

        # Calculer les totaux si lignes présentes
        if hasattr(self, 'lignes'):
            lignes = self.lignes.all()
            total_ht = sum((l.total_ht for l in lignes), Decimal('0.00'))
            total_remise = sum(((l.pu * l.quantite) - l.total_ht) for l in lignes) if lignes else Decimal('0.00')

            self.total_ht = total_ht.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_remise = total_remise.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_ht_remise = self.total_ht
            self.total_ttc = (self.total_ht * (Decimal('1') + self.tva / Decimal('100'))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            self.total_ttc_lettres = nombre_en_lettres(self.total_ttc)

            # Générer QR code
            qr_image = generate_qr_code(self.numero_devis)
            if qr_image:
                self.qr_code.save(f"qr_{self.slug}.png", qr_image, save=False)

            super().save(update_fields=[
                'total_ht', 'total_remise', 'total_ht_remise',
                'total_ttc', 'total_ttc_lettres', 'qr_code'
            ])

    def __str__(self):
        return f"{self.numero_devis} - {self.client.nom if self.client else 'Sans client'}"




class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey('Produit', on_delete=models.SET_NULL, null=True, blank=True)
    quantite = models.IntegerField(default=1)
    unite = models.CharField(max_length=20, default='unité')
    pu = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        if self.produit:
            self.pu = self.produit.prix

        super().save(*args, **kwargs)

        if self.devis:
            self.devis.save()  # recalcul des totaux

    @property
    def pu_net(self):
        return (self.pu * (Decimal('1') - self.remise / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def total_ht(self):
        return (Decimal(self.quantite) * self.pu_net).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def total_ttc(self):
        return (self.total_ht * (Decimal('1') + self.devis.tva / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.quantite} {self.unite}"