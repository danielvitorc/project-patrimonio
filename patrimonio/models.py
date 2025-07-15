from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta  
from django.utils import timezone
import base64
from django.core.files.base import ContentFile
from .utils import Base64ImageMixin  # importe o mixin

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


# Modelo para perfil de usuário com controle de admin e bloqueio
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(default=False, verbose_name='É Administrador')
    is_blocked = models.BooleanField(default=False, verbose_name='Usuário Bloqueado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - Admin: {self.is_admin} - Bloqueado: {self.is_blocked}'

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

# Signal para criar automaticamente um perfil quando um usuário é criado
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)



# Modelo para registrar atividades do sistema
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    action = models.CharField(max_length=255, verbose_name="Ação")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Registro de Atividade"
        verbose_name_plural = "Registros de Atividades"

    def __str__(self):
        return f"{self.user.username} - {self.action} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


