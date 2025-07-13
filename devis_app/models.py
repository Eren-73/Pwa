from django.db import models

# Create your models here.
from django.db import models

# Client : la personne ou entreprise à qui on fait le devis
class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    entreprise = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

# Produit ou service proposé dans un devis
class Produit(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom

# Le devis lui-même
class Devis(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Un devis appartient à un client
    date_creation = models.DateField(auto_now_add=True)
    date_expiration = models.DateField()
    statut = models.CharField(max_length=50, choices=[
        ('en_attente', 'En attente'),
        ('envoye', 'Envoyé'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ], default='en_attente')

    def __str__(self):
        return f"Devis #{self.pk} pour {self.client}"

    def montant_total(self):
        total = sum(item.sous_total() for item in self.lignes_devis.all()) # type: ignore
        return round(total, 2)

# Ligne de devis : produit + quantité
class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name="lignes_devis")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def sous_total(self):
        return self.produit.prix_unitaire * self.quantite
