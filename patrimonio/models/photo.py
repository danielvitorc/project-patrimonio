from django.db import models
from django.utils import timezone
from ..utils import Base64ImageMixin 

class Photo(models.Model, Base64ImageMixin):
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='photos/')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Foto {self.id} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def save_base64_image(self, base64_string, filename):
        """Salva a imagem base64 no campo image"""
        self.save_base64_image(base64_string, filename, self.image)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'