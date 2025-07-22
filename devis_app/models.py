from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from datetime import timedelta
import uuid

from .utils import nombre_en_lettres, generate_qr_code
from decimal import Decimal

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

    def __str__(self):
        return f"{self.prenom} {self.nom}"


def generate_numero_devis():
    return str(uuid.uuid4()).upper()[:19].replace('-', '-')


def default_date_validite():
    return now().date() + timedelta(days=30)




class Devis(models.Model):
    numero_devis = models.CharField(max_length=20, default=generate_numero_devis, unique=True)
    date_emission = models.DateField(default=now)
    date_validite = models.DateField(default=default_date_validite)
    date_proforma = models.DateField(default=now)
    regime_vente = models.CharField(max_length=10, default="TTC")
    detail_proposition = models.TextField(default='', null= True ,blank= True)

    total_ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Float remplacé par DecimalField
    total_remise = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_ht_remise = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.0'))
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_ttc_lettres = models.CharField(max_length=255, blank=True, default='')

    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # 1ère sauvegarde pour avoir un PK

        if self.pk:
            lignes = self.lignes.all()
            self.total_ht = sum(l.total_ht for l in lignes)
            self.total_remise = sum((l.pu * l.quantite - l.total_ht) for l in lignes)
            self.total_ht_remise = self.total_ht
            self.total_ttc = self.total_ht * (Decimal('1') + self.tva / Decimal('100'))
            self.total_ttc_lettres = nombre_en_lettres(self.total_ttc)

            qr_image = generate_qr_code(self.numero_devis)
            if qr_image:
                self.qr_code.save(f"qr_{slugify(self.numero_devis)}.png", qr_image, save=False)

            super().save(update_fields=[
                'total_ht', 'total_remise', 'total_ht_remise',
                'total_ttc', 'total_ttc_lettres', 'qr_code'
            ])


    def __str__(self):
        return self.numero_devis


class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, blank=True)
    quantite = models.IntegerField(default=1)
    unite = models.CharField(max_length=20, default='unité')
    pu = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    remise = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # Remplir automatiquement PU si un produit est sélectionné
        if self.produit:
            self.pu = self.produit.prix
            self.detail_proposition = self.produit.nom

        super().save(*args, **kwargs)

        # Recalculer le devis après la ligne
        if self.devis:
            self.devis.save()
    @property
    def pu_net(self):
        return self.pu * (Decimal('1') - Decimal(self.remise) / Decimal('100'))

    @property
    def total_ht(self):
        return (self.quantite * self.pu_net).quantize(Decimal("0.01"))

    @property
    def total_ttc(self):
        return (self.total_ht * (Decimal('1') + self.devis.tva / Decimal('100'))).quantize(Decimal("0.01"))


    def __str__(self):
        return f" {self.quantite} {self.unite}"
