from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta  
from django.utils import timezone

class Ocorrencia(models.Model):
    base = models.CharField(max_length=100)
    data = models.DateField(auto_now_add=True)
    ocorrencia = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tipo} - {self.base}'

class EsquecimentoCRACHA(models.Model):
    matricula = models.CharField(max_length=50)
    colaborador = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    data = models.DateField(auto_now_add=True)
    motivo = models.TextField()


    def __str__(self):
        return f'{self.colaborador} - {self.departamento}'
    
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


# models.py
class ControleChaves(models.Model):
    base = models.CharField(max_length=100)
    matricula_entregou = models.CharField(max_length=50)
    colaborador_entregou = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE)

    foto_entrega = models.ImageField(upload_to='entregas/')
    data_saida = models.DateTimeField(auto_now_add=True)

    # Campos para devolução
    matricula_recebeu = models.CharField(max_length=50, null=True, blank=True)
    colaborador_recebeu = models.CharField(max_length=100, null=True, blank=True)
    foto_devolucao = models.ImageField(upload_to='devolucoes/', null=True, blank=True)
    data_devolucao = models.DateTimeField(null=True, blank=True)

    situacao = models.CharField(max_length=100, default="RETIRADO")

    def __str__(self):
        return f'{self.matricula_entregou} - {self.situacao} - {self.chave}'



class Fornecedor(models.Model):
    CATEGORIAS = [
        ('VISITANTE', 'Visitante'),
        ('FORNECEDOR', 'Fornecedores/Prestadores de Serviços'),
        ('ENTREGA', 'Entregas'),
    ]
    STATUS_CHOICES = [
        ('Integrado', 'Integrado'),
        ('Pendente', 'Pendente'),
    ]
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Integrado')
    validade_meses = models.IntegerField(max_length=20)
    data_integracao = models.DateField(blank=True, null=True)
    data_validade = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.data_integracao:
            self.data_integracao = timezone.now().date()
        if self.validade_meses:
            from dateutil.relativedelta import relativedelta
            self.data_validade = self.data_integracao + relativedelta(months=self.validade_meses)
        if self.data_validade:
            if timezone.now().date() >= self.data_validade:
                self.status = 'Pendente'
            else:
                self.status = 'Integrado'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_categoria_display()} - ID {self.id}"

class Visitante(models.Model):
    fornecedor = models.OneToOneField(Fornecedor, on_delete=models.CASCADE, related_name='visitante')
    nome = models.CharField(max_length=255)
    documento = models.CharField(max_length=100, help_text="RG, CPF ou CNH")
    motivo_visita = models.CharField(max_length=255)
    setor_destino = models.CharField(max_length=255)
    responsavel_autorizante = models.CharField(max_length=255)
    modelo_veiculo = models.CharField(max_length=100, blank=True, null=True)
    placa_veiculo = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome


class FornecedorServico(models.Model):
    fornecedor = models.OneToOneField(Fornecedor, on_delete=models.CASCADE, related_name='fornecedor_servico')
    nome_empresa = models.CharField(max_length=255)
    nome_representante = models.CharField(max_length=255)
    documento = models.CharField(max_length=100, help_text="RG, CPF ou CNH")
    setor_destino = models.CharField(max_length=255)
    atividade_servico = models.CharField(max_length=255)
    responsavel_autorizante = models.CharField(max_length=255)
    modelo_veiculo = models.CharField(max_length=100, blank=True, null=True)
    placa_veiculo = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nome_empresa} - {self.nome_representante}"


class Entrega(models.Model):
    fornecedor = models.OneToOneField(Fornecedor, on_delete=models.CASCADE, related_name='entrega')
    tipo_entrega = models.CharField(max_length=255)
    descricao_item = models.TextField()
    quantidade_recebida = models.PositiveIntegerField()
    nome_transportadora = models.CharField(max_length=255)
    nome_entregador = models.CharField(max_length=255)
    documentos_entregador = models.CharField(max_length=255)
    placa_veiculo = models.CharField(max_length=20)
    data_hora_recebimento = models.DateTimeField()
    setor_destino = models.CharField(max_length=255)
    nome_matricula_responsavel = models.CharField(max_length=255)
    assinatura_responsavel = models.TextField(help_text="Pode armazenar assinatura digital, base64 ou texto")
    data_hora_entrega_material = models.DateTimeField()
    imagem_material = models.ImageField(upload_to='imagens_entregas/')

    def __str__(self):
        return f"Entrega {self.tipo_entrega} - {self.nome_entregador}"


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

    assinatura_portaria = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Em andamento')

    usuario_registro = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)  # opcional

    def save(self, *args, **kwargs):
        if self.status == 'Saiu' and not self.horario_saida:
            self.horario_saida = timezone.now().time()
        super().save(*args, **kwargs)

    def get_nome_fornecedor(self):
        if hasattr(self.fornecedor, 'visitante'):
            return self.fornecedor.visitante.nome
        elif hasattr(self.fornecedor, 'fornecedor_servico'):
            return self.fornecedor.fornecedor_servico.nome_empresa
        elif hasattr(self.fornecedor, 'entrega'):
            return self.fornecedor.entrega.nome_entregador
        return f"ID {self.fornecedor.id}"

    def __str__(self):
        return f"{self.get_nome_fornecedor()} - {self.data}"