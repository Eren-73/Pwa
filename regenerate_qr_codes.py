# d:\Freelance\Python_Dev\Pwa\regenerate_qr_codes.py
# Script pour régénérer tous les QR codes des devis existants
# Utile après avoir changé l'URL de base

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Devis.settings')
django.setup()

from devis_app.models import Devis
from devis_app.utils import generate_qr_code

def regenerate_all_qr_codes():
    """Régénère tous les QR codes pour tous les devis."""
    devis_list = Devis.objects.all()
    total = devis_list.count()
    success_count = 0
    error_count = 0
    
    print(f"🔄 Régénération des QR codes pour {total} devis...\n")
    
    for i, devis in enumerate(devis_list, 1):
        try:
            # Générer le nouveau QR code
            qr_image = generate_qr_code(devis.slug)
            
            if qr_image:
                # Sauvegarder le QR code
                devis.qr_code.save(f"qr_{devis.slug}.png", qr_image, save=False)
                devis.save(update_fields=['qr_code'])
                
                print(f"✅ [{i}/{total}] QR code généré pour le devis {devis.numero_devis}")
                success_count += 1
            else:
                print(f"⚠️ [{i}/{total}] Échec de génération pour {devis.numero_devis}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ [{i}/{total}] Erreur pour {devis.numero_devis}: {str(e)}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Succès: {success_count}/{total}")
    print(f"❌ Erreurs: {error_count}/{total}")
    print(f"{'='*50}")

if __name__ == "__main__":
    regenerate_all_qr_codes()
