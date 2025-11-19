from django.db import models

class EsquecimentoCRACHA(models.Model):
    matricula = models.CharField(max_length=50)
    colaborador = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    data = models.DateField(auto_now_add=True)
    motivo = models.TextField()


    def __str__(self):
        return f'{self.colaborador} - {self.departamento}'