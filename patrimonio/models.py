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


class Chave(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class ControleChaves(models.Model):
    base = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50)
    colaborador = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    situacao = models.CharField(max_length=100, default="RETIRADO")
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.matricula} - {self.situacao} - {self.chave}'


class Fornecedor(models.Model):
    cpf = models.CharField(max_length=18)
    nome = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ('Integrado', 'Integrado'),
        ('Pendente', 'Pendente'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Integrado')
    validade_meses = models.IntegerField()
    data_integracao = models.DateField()
    validade_meses = models.IntegerField(help_text="Validade em meses")
    data_integracao = models.DateField(blank=True, null=True)
    data_validade = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.data_integracao:
            self.data_integracao = date.today()

        if self.validade_meses:
            self.data_validade = self.data_integracao + relativedelta(months=self.validade_meses)

        # Atualiza status
        if self.data_validade:
            if date.today() >= self.data_validade:
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
    
class EntradaFornecedorAvulso(models.Model):
    STATUS_CHOICES = [
        ('Em andamento', 'Em andamento'),
        ('Saiu', 'Saiu'),
    ]

    data = models.DateField(auto_now_add=True)
    horario_entrada = models.TimeField(auto_now_add=True)
    horario_saida = models.TimeField(null=True, blank=True)

    base = models.CharField(max_length=100)
    fornecedor_nome = models.CharField(max_length=100)  # Nome digitado do fornecedor avulso
    cpf_ou_cnpj = models.CharField(max_length=20)       # CPF ou CNPJ digitado manualmente
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
        return f"{self.fornecedor_nome} - {self.data}"

    def emitiu_alerta_validade(self):
        """Retorna True se está a 7 dias ou menos do vencimento."""
        if self.data_validade:
            dias_restantes = (self.data_validade - date.today()).days
            return dias_restantes <= 7 and dias_restantes >= 0
        return False

    def __str__(self):
        return f"{self.nome} ({self.cnpj})"
