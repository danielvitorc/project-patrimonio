from django.db import models

class Colaborador(models.Model):
    matricula = models.CharField(max_length=50)
    nome = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.matricula} - {self.nome}'