from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from datetime import timedelta
import uuid
from django.db.models import Max

from .utils import  generate_qr_code,nombre_en_lettres
from decimal import Decimal,ROUND_HALF_UP
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User


class PointVente(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nom

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('commercial', 'Commercial'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    point_vente = models.ForeignKey(PointVente, on_delete=models.SET_NULL, null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


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
    # Main user reference - for the commercial who created the devis
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devis", null=True, blank=True)
    point_vente = models.ForeignKey(PointVente, on_delete=models.SET_NULL, null=True, blank=True)
    numero_devis = models.CharField(max_length=20, unique=True, blank=True)
    date_emission = models.DateField(default=now)
    date_validite = models.DateField(default=default_date_validite)
    date_proforma = models.DateField(default=now)
    appliquer_tva = models.BooleanField(default=True)  # <---- Nouveau champ
    REGIME_CHOICES = [
        ('TTC (CFA)', 'TTC (CFA)'),
    ]
    regime_vente = models.CharField(
        max_length=50, 
        choices=REGIME_CHOICES,
        default="TTC (CFA)"
    )
    detail_proposition = models.TextField(default='', null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    total_ht = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ht_remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    total_tva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))  # <--- Ajouté
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ttc_lettres = models.CharField(max_length=255, blank=True, default='')

    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True, related_name="devis")
    
    def save(self, *args, **kwargs):
        # --- Génération numéro devis (inchangé) ---
        if not self.numero_devis:
            today = now().date()
            year, month, day = today.year, today.month, today.day

            last_devis = Devis.objects.filter(
                date_emission__year=year,
                date_emission__month=month,
                date_emission__day=day
            ).aggregate(Max('numero_devis'))['numero_devis__max']

            if last_devis:
                try:
                    last_counter = int(last_devis.split('-')[-1])
                except (IndexError, ValueError):
                    last_counter = 0
                counter = last_counter + 1
            else:
                counter = 1

            self.numero_devis = f"{year}-{month:02d}-{day:02d}-{counter:05d}"

        if not self.slug:
            self.slug = slugify(self.numero_devis)

        super().save(*args, **kwargs)

        # --- Calcul des totaux ---
        if hasattr(self, 'lignes'):
            lignes = self.lignes.all()

            total_ht_brut = sum((l.pu * l.quantite) for l in lignes) if lignes else Decimal('0.00')
            total_remise = sum(((l.pu * l.quantite) - l.total_ht) for l in lignes) if lignes else Decimal('0.00')
            total_ht_net = total_ht_brut - total_remise

            # Appliquer TVA seulement si appliquer_tva = True
            if self.appliquer_tva:
                tva_amount = (total_ht_net * (self.tva / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                tva_amount = Decimal('0.00')

            total_ttc = total_ht_net + tva_amount

            self.total_ht = total_ht_brut.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_remise = total_remise.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_ht_remise = total_ht_net.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_tva = tva_amount
            self.total_ttc = total_ttc.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.total_ttc_lettres = nombre_en_lettres(self.total_ttc)

            # Générer le QR code avec le slug du devis
            qr_image = generate_qr_code(self.slug)
            if qr_image:
                self.qr_code.save(f"qr_{self.slug}.png", qr_image, save=False)

            super().save(update_fields=[
                'total_ht', 'total_remise', 'total_ht_remise',
                'total_tva', 'total_ttc', 'total_ttc_lettres', 'qr_code'
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
    



class ActionCommercial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    date_action = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} ({self.date_action.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = "Action du commercial"
        verbose_name_plural = "Actions des commerciaux"
        ordering = ['-date_action']
