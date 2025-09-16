from django.contrib.auth.models import User 
from django.db import models
from django.utils import timezone
from ..utils import Base64ImageMixin

class Fornecedor(models.Model):
    CATEGORIAS = [
        ('VISITANTE', 'Visitante'),
        ('FORNECEDOR', 'Fornecedores/Prestadores de Serviços'),
    ]
    STATUS_CHOICES = [
        ('Integrado', 'Integrado'),
        ('Pendente', 'Pendente'),
    ]
    
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Integrado')
    validade_meses = models.IntegerField()
    data_integracao = models.DateField(blank=True, null=True)
    data_validade = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.data_integracao:
            self.data_integracao = timezone.now().date()
        if self.validade_meses:
            from dateutil.relativedelta import relativedelta
            self.data_validade = self.data_integracao + relativedelta(months=self.validade_meses)
        if self.data_validade:
            self.status = 'Pendente' if timezone.now().date() >= self.data_validade else 'Integrado'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_categoria_display()} - ID {self.id}"

class Visitante(models.Model, Base64ImageMixin):
    fornecedor = models.OneToOneField(Fornecedor, on_delete=models.CASCADE, related_name='visitante')
    nome = models.CharField(max_length=255)
    documento = models.CharField(max_length=100, help_text="RG, CPF ou CNH")
    motivo_visita = models.CharField(max_length=255)
    foto_visitante = models.ImageField(upload_to='fotos_visitantes/', blank=True, null=True)

    def save_base64_image(self, base64_string, filename):
        """Salva a imagem base64 no campo foto_visitante"""
        self.save_base64_image(base64_string, filename, self.foto_visitante)

    def __str__(self):
        return f"{self.nome} ({self.documento})"

class FornecedorServico(models.Model):
    fornecedor = models.OneToOneField(Fornecedor, on_delete=models.CASCADE, related_name='fornecedor_servico')
    nome_empresa = models.CharField(max_length=255)
    nome_representante = models.CharField(max_length=255)
    documento = models.CharField(max_length=100, help_text="RG, CPF ou CNH")
    atividade_servico = models.CharField(max_length=255)
    # Campos removidos: setor_destino, responsavel_autorizante, modelo_veiculo, placa_veiculo
    foto_fornecedor = models.ImageField(upload_to='fotos_fornecedores/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome_empresa} - {self.nome_representante}"

class Entrega(models.Model):
    fornecedor = models.OneToOneField(Fornecedor, on_delete=models.CASCADE, related_name='entrega')
    tipo_entrega = models.CharField(max_length=255)
    descricao_item = models.TextField()
    nome_transportadora = models.CharField(max_length=255)
    nome_entregador = models.CharField(max_length=255)
    documentos_entregador = models.CharField(max_length=255)
    data_hora_recebimento = models.DateTimeField()
    nome_matricula_responsavel = models.CharField(max_length=255)
    assinatura_responsavel = models.TextField(help_text="Pode armazenar assinatura digital, base64 ou texto")
    data_hora_entrega_material = models.DateTimeField()
    foto_caixa_entrega = models.ImageField(upload_to='fotos_entregas/', blank=True, null=True)

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

    # Campos adicionados no formulário de entrada
    setor_destino = models.CharField(max_length=255)
    responsavel_autorizante = models.CharField(max_length=100, null=True, blank=True)
    modelo_veiculo = models.CharField(max_length=100, blank=True, null=True)
    placa_veiculo = models.CharField(max_length=20, blank=True, null=True)

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