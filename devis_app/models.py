from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from datetime import timedelta
import uuid

from .utils import  generate_qr_code,nombre_en_lettres
from decimal import Decimal,ROUND_HALF_UP

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

    def __str__(self):
        return f"{self.prenom} {self.nom}"


def generate_numero_devis():
    return str(uuid.uuid4()).upper()[:19].replace('-', '-')


def default_date_validite():
    return now().date() + timedelta(days=30)



class Devis(models.Model):
    numero_devis = models.CharField(max_length=20, unique=True, blank=True)
    date_emission = models.DateField(default=now)
    date_validite = models.DateField(default=default_date_validite)
    date_proforma = models.DateField(default=now)
    regime_vente = models.CharField(max_length=10, default="TTC")
    detail_proposition = models.TextField(default='', null=True, blank=True)

    total_ht = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ht_remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ttc_lettres = models.CharField(max_length=255, blank=True, default='')

    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True, related_name="devis")

    def save(self, *args, **kwargs):
        # Génération automatique du numéro
        if not self.numero_devis:
            today = now().date()
            prefix = today.strftime("%Y-%m")
            last_devis = Devis.objects.filter(
                date_emission__year=today.year,
                date_emission__month=today.month
            ).order_by('id').last()

            if last_devis and last_devis.numero_devis.startswith(prefix):
                last_number = int(last_devis.numero_devis.split('-')[-1])
                next_number = last_number + 1
            else:
                next_number = 1

            self.numero_devis = f"{prefix}-{str(next_number).zfill(5)}"

        super().save(*args, **kwargs)  # 1ère sauvegarde pour obtenir un PK

        if self.pk:
            lignes = self.lignes.all()

            # Forcer sum à retourner un Decimal
            total_ht = sum((l.total_ht for l in lignes), Decimal('0.00'))
            total_remise = sum(
                ((l.pu * l.quantite) - l.total_ht) for l in lignes
            ) if lignes else Decimal('0.00')

            self.total_ht = total_ht.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_remise = total_remise.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_ht_remise = self.total_ht
            self.total_ttc = (self.total_ht * (Decimal('1') + self.tva / Decimal('100'))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
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