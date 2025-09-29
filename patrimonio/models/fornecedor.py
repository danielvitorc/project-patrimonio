from django.contrib.auth.models import User 
from django.db import models
from django.utils import timezone
from patrimonio.utils import Base64ImageMixin
from dateutil.relativedelta import relativedelta


class Fornecedor(models.Model):
    CATEGORIAS = [
        ('VISITANTE', 'Visitante'),
        ('FORNECEDOR', 'Fornecedores/Prestadores de Serviços'),
    ]

    SUBCATEGORIAS = [
        ('CLT', 'Trabalhador CLT'),
        ('PJ', 'Pessoa Jurídica (PJ)'),
        ('MEI', 'Microempreendedor Individual (MEI)'),
        ('AUTONOMO', 'Autônomo'),
        ('ASSOCIADO', 'Associado'),
    ]

    STATUS_CHOICES = [
        ('Integrado', 'Integrado'),
        ('Pendente', 'Pendente'),
    ]
    
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    subcategoria = models.CharField(max_length=20, choices=SUBCATEGORIAS, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Integrado')
    validade_meses = models.IntegerField()
    data_integracao = models.DateField(blank=True, null=True)
    data_validade = models.DateField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            if not self.data_integracao:
                self.data_integracao = timezone.now().date()
            if self.validade_meses:
                self.data_validade = self.data_integracao + relativedelta(months=self.validade_meses)
        
        if self.data_validade:
            self.status = 'Pendente' if timezone.now().date() >= self.data_validade else 'Integrado'
        super().save(*args, **kwargs)
        
    def __str__(self):
        # Tenta obter o nome do visitante, se existir
        if self.categoria == 'VISITANTE' and hasattr(self, 'visitante'):
            return f"Visitante: {self.visitante.nome}"
        
        # Tenta obter o nome da empresa/representante do fornecedor de serviço
        if self.categoria == 'FORNECEDOR' and hasattr(self, 'trabalhador_relacionado'):
            # O 'trabalhador_relacionado' é uma property que você já deve ter
            # para buscar o representante em diferentes tabelas (CLT, PJ, etc.)
            trabalhador = self.trabalhador_relacionado
            if trabalhador:
                # Se tiver nome da empresa e do representante
                if hasattr(self, 'fornecedor_servico') and self.fornecedor_servico.nome_empresa:
                    return f"{self.fornecedor_servico.nome_empresa} ({trabalhador.nome_representante})"
                # Se tiver só o nome do representante
                return f"Fornecedor: {trabalhador.nome_representante}"

        # Fallback: se não encontrar um nome específico, retorna o ID
        return f"Fornecedor ID {self.pk}"

    @property
    def trabalhador_relacionado(self):
        if self.subcategoria == 'CLT':
            return self.trabalhadores_clt.first()
        if self.subcategoria == 'PJ':
            return self.pessoas_juridicas.first()
        if self.subcategoria == 'MEI':
            return self.meis.first()
        if self.subcategoria == 'AUTONOMO':
            return self.autonomos.first()
        if self.subcategoria == 'ASSOCIADO':
            return self.associados.first()
        
        return None





# Seu modelo original, com pequenos ajustes e relacionamento a Fornecedor
class FornecedorServico(models.Model):
    fornecedor = models.OneToOneField(Fornecedor, on_delete=models.CASCADE, related_name='fornecedor_servico')
    nome_empresa = models.CharField(max_length=255)
    atividade_servico = models.CharField(max_length=255)
    # O campo foto_fornecedor foi movido para os modelos de trabalhadores individuais
    # para representar a foto da pessoa física (representante).

    def __str__(self):
        return self.nome_empresa

# --- Modelos para os Tipos de Trabalhadores ---

# Classe base abstrata para compartilhar campos comuns
class BaseTrabalhador(models.Model):
    """
    Modelo abstrato que contém os campos comuns para todos os tipos de trabalhadores.
    Não cria uma tabela no banco de dados. [1, 4]
    """
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='trabalhadores')
    nome_representante = models.CharField(max_length=255)
    documento_identificacao = models.FileField(
        upload_to='documentos/identificacao/',
        help_text="Documento de identificação com foto (CPF, RG ou CNH)"
    )
    foto_representante = models.ImageField(
        upload_to='documentos/fotos_representantes/',
        blank=True, null=True,
        help_text="Captura de Foto do Representante"
    )
    carteira_orgao_profissional = models.FileField(
        upload_to='documentos/carteiras_profissionais/',
        blank=True, null=True,
        help_text="Carteira do órgão profissional (quando aplicável)"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome_representante

# Modelo para Trabalhador CLT
class TrabalhadorCLT(BaseTrabalhador):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='trabalhadores_clt')
    descricao_cargo = models.CharField(max_length=255)
    aso = models.FileField(upload_to='documentos/clt/aso/', help_text="Atestado de saúde ocupacional – ASO mais recente")
    ordem_servico = models.FileField(upload_to='documentos/clt/ordem_servico/', help_text="Ordem de Serviço, por função")
    pgr = models.FileField(upload_to='documentos/clt/pgr/', help_text="Programa de Gerenciamento de Riscos – PGR")
    pcmso = models.FileField(upload_to='documentos/clt/pcmso/', help_text="Programa de Controle Médico de Saúde Ocupacional – PCMSO")
    certificados_treinamentos = models.FileField(upload_to='documentos/clt/certificados/', help_text="Certificados e treinamentos conforme o risco e atividade")
    cautela_epi_epc = models.FileField(upload_to='documentos/clt/cautela_epi/', help_text="Cautela de EPI e EPC")
    apr_pt = models.FileField(upload_to='documentos/clt/apr_pt/', help_text="Análise Preliminar de Risco - APR ou Permissão de trabalho – PT")

    class Meta:
        verbose_name = "Trabalhador CLT"
        verbose_name_plural = "Trabalhadores CLT"


# Modelo para Pessoa Jurídica (PJ)
class PessoaJuridica(BaseTrabalhador):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='pessoas_juridicas')
    cnpj = models.FileField(upload_to='documentos/pj/cnpj/', help_text="Cadastro Nacional de Pessoa Jurídica (CNPJ)")
    contrato_prestacao_servico = models.FileField(upload_to='documentos/pj/contratos/', help_text="Contrato de prestação de serviço com a assessoria contratante")

    class Meta:
        verbose_name = "Pessoa Jurídica (PJ)"
        verbose_name_plural = "Pessoas Jurídicas (PJ)"


# Modelo para Microempreendedor Individual (MEI)
class MEI(BaseTrabalhador):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='meis')
    certificado_mei = models.FileField(upload_to='documentos/mei/certificados/', help_text="Certificado da condição de Microempreendedor Individual")
    contrato_prestacao_servico = models.FileField(upload_to='documentos/mei/contratos/', help_text="Contrato de prestação de serviço com a assessoria contratante")

    class Meta:
        verbose_name = "Microempreendedor Individual (MEI)"
        verbose_name_plural = "Microempreendedores Individuais (MEI)"


# Modelo para Autônomo
class Autonomo(BaseTrabalhador):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='autonomos')
    declaracao_autonomo = models.FileField(upload_to='documentos/autonomo/declaracoes/', help_text="Declaração de autônomo - registro na Prefeitura Municipal")
    contrato_prestacao_servico = models.FileField(upload_to='documentos/autonomo/contratos/', help_text="Contrato de prestação de serviço com a assessoria contratante")

    class Meta:
        verbose_name = "Autônomo"
        verbose_name_plural = "Autônomos"

# Modelo para Associado
class Associado(BaseTrabalhador):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='associados')
    contrato_associacao = models.FileField(
        upload_to='documentos/associado/contratos/', 
        help_text="Contrato de associação"
    )

    class Meta:
        verbose_name = "Associado"
        verbose_name_plural = "Associados"


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