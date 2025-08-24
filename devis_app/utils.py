import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from num2words import num2words
from django.urls import reverse


def generate_qr_code(numero_devis):
    base_url = "http://192.168.1.20:8000/detail/"  # ou ton URL en prod
    content = f"{base_url}{numero_devis}/"   # ex: http://192.168.1.20:8000/detail/4270F6EB-5350-4623

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
def generate_qr_for_facture(facture):
    url = f"http://192.168.1.20:8000{reverse('detail_facture', args=[facture.id])}"
    return generate_qr_code(url) 