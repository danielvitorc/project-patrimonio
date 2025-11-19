from django.db import models

class Chave(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class ControleChaves(models.Model):
    base = models.CharField(max_length=100)
    matricula_recebendo = models.CharField(max_length=50)
    colaborador_recebendo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE)

    foto_entrega = models.ImageField(upload_to='entregas/')
    data_saida = models.DateTimeField(auto_now_add=True)

    # Campos para devolução
    matricula_devolveu = models.CharField(max_length=50, null=True, blank=True)
    colaborador_devolveu = models.CharField(max_length=100, null=True, blank=True)
    foto_devolucao = models.ImageField(upload_to='devolucoes/', null=True, blank=True)
    data_devolucao = models.DateTimeField(null=True, blank=True)

    situacao = models.CharField(max_length=100, default="RETIRADO")

    def __str__(self):
        return f'{self.matricula_recebendo} - {self.situacao} - {self.chave}'