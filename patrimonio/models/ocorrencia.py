from django.contrib.auth.models import User
from django.db import models

class Ocorrencia(models.Model):
    base = models.CharField(max_length=100)
    data = models.DateField(auto_now_add=True)
    ocorrencia = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tipo} - {self.base}'