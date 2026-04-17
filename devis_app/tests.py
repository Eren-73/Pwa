"""
Fichier : devis_app/tests.py
Description :
Ce fichier contient les tests unitaires pour l'application devis_app.
Il permet de vérifier la création d'un devis et la cohérence des données en base.

Procédure pour exécuter les tests :
1. Ouvrir un terminal dans le dossier du projet.
2. Activer l'environnement virtuel si besoin.
3. Lancer la commande suivante :
	python manage.py test devis_app -v 2

Résultat attendu :
Tous les tests doivent passer sans erreur (OK).

Auteur : Traore Husseni 
Date : [Date de modification]
"""

from django.test import TestCase
from devis_app.models import Client, Devis
from devis_app.utils import normalize_phone_for_whatsapp
from django.utils import timezone

class DevisModelTest(TestCase):
	def setUp(self):
		self.client_obj = Client.objects.create(
			nom="Test",
			prenom="User",
			email="testuser@example.com",
			telephone="0123456789",
			adresse="Test Address"
		)

	def test_create_devis(self):
		devis = Devis.objects.create(
			client=self.client_obj,
			numero_devis="DEV-001",
			date_emission=timezone.now(),
			total_ht=1000,
			total_remise=0,
			total_ht_remise=1000,
			total_tva=180,
			total_ttc=1180,
			regime_vente="Normal",
			date_proforma=timezone.now(),
			date_validite=timezone.now(),
		)
		self.assertEqual(Devis.objects.count(), 1)
		self.assertEqual(devis.client.nom, "Test")


class WhatsAppPhoneTest(TestCase):
	def test_normalize_ci_local_number(self):
		self.assertEqual(normalize_phone_for_whatsapp("0546858286"), "2250546858286")

	def test_repair_old_ci_number_without_zero(self):
		self.assertEqual(normalize_phone_for_whatsapp("225546858286"), "2250546858286")

	def test_client_phone_is_normalized_on_save(self):
		client = Client.objects.create(
			nom="Dao",
			prenom="Malick",
			email="malick@example.com",
			telephone="0546858286",
			adresse="Abidjan",
		)
		self.assertEqual(client.telephone, "2250546858286")
