from django.db import models
from django.contrib.auth.models import User

class Ocorrencia(models.Model):
    base = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    ocorrencia = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tipo} - {self.base}'

class Colaborador(models.Model):
    matricula = models.CharField(max_length=50)
    nome = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.matricula} - {self.nome}'

class ControleChaves(models.Model):
    base = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50)
    colaborador = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    situacao = models.CharField(max_length=100, default="RETIRADO")

    def __str__(self):
        return f'{self.matricula} - {self.situacao}'

