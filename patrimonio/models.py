from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta  

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


class Fornecedor(models.Model):
    cnpj = models.CharField(max_length=18)
    nome = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ('Integrado', 'Integrado'),
        ('Pendente', 'Pendente'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Integrado')
    validade_meses = models.IntegerField()
    data_integracao = models.DateField()
    data_validade = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.data_integracao:
            self.data_integracao = date.today()

        # Calcula a data de validade a partir da data de integração + meses
        if self.validade_meses:
            self.data_validade = self.data_integracao + relativedelta(months=self.validade_meses)

        # Atualiza status com base na validade
        if self.data_validade and date.today() >= self.data_validade:
            self.status = 'Pendente'
        else:
            self.status = 'Integrado'

        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.nome


class EntradaFornecedor(models.Model):
    STATUS_CHOICES = [
        ('Em andamento', 'Em andamento'),
        ('Saiu', 'Saiu'),
    ]

    data = models.DateField(auto_now_add=True)
    horario_entrada = models.TimeField(auto_now_add=True)
    horario_saida = models.TimeField(null=True, blank=True)

    base = models.CharField(max_length=100)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='entradas')
    quantidade = models.IntegerField()
    visitantes = models.TextField()
    tipo_documento = models.TextField()
    documento = models.TextField()
    setor = models.CharField(max_length=100)
    responsavel = models.CharField(max_length=100)
    assinatura_portaria = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Em andamento')

    def save(self, *args, **kwargs):
        if self.status == 'Saiu' and self.horario_saida is None:
            self.horario_saida = datetime.now().time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fornecedor.nome} - {self.data}"