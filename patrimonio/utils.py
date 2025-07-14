import base64
from django.core.files.base import ContentFile

class Base64ImageMixin:
    def save_base64_image(self, base64_string, filename, image_field):
        """Salva uma imagem base64 no campo especificado"""
        format, imgstr = base64_string.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f"{filename}.{ext}")
        image_field.save(f"{filename}.{ext}", data, save=False)
import base64
import uuid
from django.core.files.base import ContentFile

def process_webcam_photo(base64_data, prefix='foto'):
    if base64_data.startswith('data:image'):
        format, imgstr = base64_data.split(';base64,')  # divide o cabeçalho do conteúdo
        ext = format.split('/')[-1]
        file_name = f"{prefix}_{uuid.uuid4().hex[:10]}.{ext}"
        return ContentFile(base64.b64decode(imgstr), name=file_name)
    return None