import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from num2words import num2words
from django.urls import reverse
from django.conf import settings
import re


def generate_qr_code(devis_slug):
    """
    Génère un QR code qui pointe vers la page de détail du devis.
    Le slug du devis est utilisé pour construire l'URL.
    L'URL est construite à partir de SITE_URL dans settings.py
    """
    # Récupérer l'URL de base depuis les settings
    base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    
    # Construire l'URL complète vers la page de détail du devis
    content = f"{base_url}/facture/{devis_slug}/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


# 🔹 Ajouter cette fonction pour convertir un nombre en lettres
def nombre_en_lettres(nombre):
    try:
        return num2words(nombre, lang='fr').capitalize()
    except:
        return ""


def normalize_phone_for_whatsapp(value):
    if not value:
        return ''

    digits = re.sub(r'\D+', '', str(value))
    if not digits:
        return ''

    if digits.startswith('00'):
        digits = digits[2:]

    if len(digits) == 10 and digits.startswith('0'):
        return f'225{digits[1:]}'

    if len(digits) == 13 and digits.startswith('00225'):
        return digits[2:]

    return digits
def generate_qr_for_facture(facture):
    url = f"http://192.168.1.20:8000{reverse('detail_facture', args=[facture.id])}"
    return generate_qr_code(url) 