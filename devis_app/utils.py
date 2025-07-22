import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from num2words import num2words


def generate_qr_code(content):
    qr = qrcode.make(content)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


def nombre_en_lettres(nombre):
    try:
        return num2words(nombre, lang='fr').capitalize()
    except:
        return ""
