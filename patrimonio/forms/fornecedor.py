from django import forms
from django_select2.forms import Select2Widget 
from patrimonio.models import Fornecedor, Visitante, FornecedorServico, Entrega, EntradaFornecedor, TrabalhadorCLT, PessoaJuridica, MEI, Autonomo, Associado, QuestionarioIntegracao
from ._choices import BASE_CHOICES


BASE_CHOICES = [
    ('BASE TARUMÃ', 'BASE TARUMÃ'),
    ('BASE FLORES', 'BASE FLORES'),
    ('BASE PONTA NEGRA', 'BASE PONTA NEGRA'),
    ('BASE SÃO JOSÉ', 'BASE SÃO JOSÉ'),
    ('BASE CIDADE NOVA', 'BASE CIDADE NOVA')
]

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['categoria', 'subcategoria']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # restringe choices só para Visitante
        self.fields['categoria'].choices = [('VISITANTE', 'Visitante')]
        self.fields['categoria'].initial = 'VISITANTE'
        # opcional: esconder subcategoria para Visitante
        self.fields['subcategoria'].widget = forms.HiddenInput()
        self.fields['subcategoria'].required = False


# Seu formulário inicial (com uma pequena modificação)
class FornecedorPrestadorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['subcategoria']
        widgets = {
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'subcategoria': 'Selecione a Subcategoria',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.categoria = 'FORNECEDOR'
        if commit:
            instance.save()
        return instance


# 🔹 Form para Trabalhador CLT - CORRIGIDO
class TrabalhadorCLTForm(forms.ModelForm):
    class Meta:
        model = TrabalhadorCLT
        exclude = ['fornecedor']  # Excluir o campo fornecedor
        widgets = {
            'nome_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_identificacao': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_representante': forms.FileInput(attrs={'class': 'form-control'}),
            'carteira_orgao_profissional': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao_cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'aso': forms.FileInput(attrs={'class': 'form-control'}),
            'ordem_servico': forms.FileInput(attrs={'class': 'form-control'}),
            'pgr': forms.FileInput(attrs={'class': 'form-control'}),
            'pcmso': forms.FileInput(attrs={'class': 'form-control'}),
            'certificados_treinamentos': forms.FileInput(attrs={'class': 'form-control'}),
            'cautela_epi_epc': forms.FileInput(attrs={'class': 'form-control'}),
            'apr_pt': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos opcionais exceto nome_representante
        for field_name, field in self.fields.items():
            if field_name != 'nome_representante':
                field.required = False


# 🔹 Form para Pessoa Jurídica (PJ) - CORRIGIDO
class PessoaJuridicaForm(forms.ModelForm):
    class Meta:
        model = PessoaJuridica
        exclude = ['fornecedor']  # Excluir o campo fornecedor
        widgets = {
            'nome_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_identificacao': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_representante': forms.FileInput(attrs={'class': 'form-control'}),
            'carteira_orgao_profissional': forms.FileInput(attrs={'class': 'form-control'}),
            'cnpj': forms.FileInput(attrs={'class': 'form-control'}),
            'contrato_prestacao_servico': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos opcionais exceto nome_representante
        for field_name, field in self.fields.items():
            if field_name != 'nome_representante':
                field.required = False


# 🔹 Form para Microempreendedor Individual (MEI) - CORRIGIDO
class MEIForm(forms.ModelForm):
    class Meta:
        model = MEI
        exclude = ['fornecedor']  # Excluir o campo fornecedor
        widgets = {
            'nome_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_identificacao': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_representante': forms.FileInput(attrs={'class': 'form-control'}),
            'carteira_orgao_profissional': forms.FileInput(attrs={'class': 'form-control'}),
            'certificado_mei': forms.FileInput(attrs={'class': 'form-control'}),
            'contrato_prestacao_servico': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos opcionais exceto nome_representante
        for field_name, field in self.fields.items():
            if field_name != 'nome_representante':
                field.required = False


# 🔹 Form para Autônomo - CORRIGIDO
class AutonomoForm(forms.ModelForm):
    class Meta:
        model = Autonomo
        exclude = ['fornecedor']  # Excluir o campo fornecedor
        widgets = {
            'nome_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_identificacao': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_representante': forms.FileInput(attrs={'class': 'form-control'}),
            'carteira_orgao_profissional': forms.FileInput(attrs={'class': 'form-control'}),
            'declaracao_autonomo': forms.FileInput(attrs={'class': 'form-control'}),
            'contrato_prestacao_servico': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos opcionais exceto nome_representante
        for field_name, field in self.fields.items():
            if field_name != 'nome_representante':
                field.required = False


# 🔹 Form para Associado - CORRIGIDO
class AssociadoForm(forms.ModelForm):
    class Meta:
        model = Associado
        exclude = ['fornecedor']  # Excluir o campo fornecedor
        widgets = {
            'nome_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_identificacao': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_representante': forms.FileInput(attrs={'class': 'form-control'}),
            'carteira_orgao_profissional': forms.FileInput(attrs={'class': 'form-control'}),
            'contrato_associacao': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos opcionais exceto nome_representante
        for field_name, field in self.fields.items():
            if field_name != 'nome_representante':
                field.required = False


# 🔹 Form para Fornecedor de Serviço - CORRIGIDO
class FornecedorServicoForm(forms.ModelForm):
    class Meta:
        model = FornecedorServico
        exclude = ['fornecedor']  # Excluir o campo fornecedor
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'atividade_servico': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos opcionais exceto nome_empresa
        for field_name, field in self.fields.items():
            if field_name != 'nome_empresa':
                field.required = False


class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        exclude = ['fornecedor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo_visita': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_visitante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



class EntregaForm(forms.ModelForm):
    foto_webcam = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="Foto capturada via webcam"
    )

    class Meta:
        model = Entrega
        exclude = ['fornecedor']
        widgets = {
            'tipo_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_item': forms.Textarea(attrs={'class': 'form-control'}),
            'nome_transportadora': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_entregador': forms.TextInput(attrs={'class': 'form-control'}),
            'documentos_entregador': forms.TextInput(attrs={'class': 'form-control'}),
            'data_hora_recebimento': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'nome_matricula_responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'assinatura_responsavel': forms.Textarea(attrs={'class': 'form-control'}),
            'data_hora_entrega_material': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'foto_caixa_entrega': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class EntradaFornecedorForm(forms.ModelForm):
    base = forms.ChoiceField(
        choices=BASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # 1. Defina o campo 'fornecedor' aqui, fora do Meta.
    #    Isso nos dá controle total sobre ele.
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.none(), # Será preenchido no __init__
        label="Fornecedor",
        widget=Select2Widget(attrs={
            'class': 'form-input', 
            'data-dropdown-parent': '#modalEntradaFornecedorOverlay', # ID do modal
            'data-placeholder': 'Digite o nome para buscar...', # Texto de ajuda
            'style': 'width: 100%', # Força ocupar o espaço todo
        })
    )

    class Meta:
        model = EntradaFornecedor
        # 2. Liste os campos. O campo 'fornecedor' que definimos acima será usado.
        fields = [
            'fornecedor', 
            'base', 
            'setor_destino', 
            'responsavel_autorizante', 
            'modelo_veiculo', 
            'placa_veiculo',
            'assinatura_portaria' # Adicionei este campo que estava no seu Meta original
        ]
        widgets = {
            # 3. Defina os widgets para os OUTROS campos.
            'base': forms.Select(attrs={'class': 'form-control'}),
            'setor_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_autorizante': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'placa_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'assinatura_portaria': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega o queryset ordenado que a view passou
        queryset_ordenado = kwargs.pop('queryset', None)
        super().__init__(*args, **kwargs)

        # 4. Se a view passou um queryset, nós o usamos.
        if queryset_ordenado is not None:
            self.fields['fornecedor'].queryset = queryset_ordenado

        # 5. Define a função que transforma o objeto (Fornecedor) em texto no dropdown.
        self.fields['fornecedor'].label_from_instance = self.label_fornecedor

    def label_fornecedor(self, obj):
        """
        Define o texto que será exibido para cada fornecedor no dropdown.
        """
        # 1. Trata o caso do Visitante (que já está funcionando)
        if obj.categoria == 'VISITANTE' and hasattr(obj, 'visitante') and obj.visitante:
            return f"Visitante: {obj.visitante.nome}"
        
        # 2. Trata o caso do Fornecedor (LÓGICA REFINADA)
        if obj.categoria == 'FORNECEDOR':
            # Pega o trabalhador usando a property que criamos no models.py
            trabalhador = obj.trabalhador_relacionado
            
            # Se um trabalhador foi encontrado...
            if trabalhador and trabalhador.nome_representante:
                nome_empresa = None
                # Tenta pegar o nome da empresa de forma segura
                if hasattr(obj, 'fornecedor_servico') and obj.fornecedor_servico:
                    nome_empresa = obj.fornecedor_servico.nome_empresa

                # Monta a string final
                if nome_empresa:
                    return f"{nome_empresa} ({trabalhador.nome_representante})"
                else:
                    # Se não tiver empresa, mostra só o nome do representante
                    return f"Fornecedor: {trabalhador.nome_representante}"

        # 3. Fallback: Se nada funcionar, mostra o ID.
        # Isso nos ajuda a saber quais objetos estão com dados faltando.
        return f"Cadastro ID {obj.pk}"

# choices e respostas corretas (ajuste o texto conforme seu conteúdo)
Q1_CHOICES = [
    ('A', 'A: Usar shorts e sandálias para maior conforto.'),
    ('B', 'B: Respeitar placas de sinalização, utilizar crachá visível, não obstruir saídas de emergência e utilizar EPIs de acordo com o risco da atividade.'),
    ('C', 'C: Falar ao celular enquanto sobe escadas.'),
]

Q2_CHOICES = [
    ('A', 'A: Evacuar imediatamente e dirigir-se a um dos pontos de encontro definidos.'),
    ('B', 'B: Utilizar elevadores para agilizar a saída'),
    ('C', 'C: Permanecer no posto de trabalho aguardando instruções.'),
]

Q3_CHOICES = [
    ('A', 'A: Respeito e empatia entre colegas.'),
    ('B', 'B: Cumprimento das normas de segurança.'),
    ('C', 'C:  Assédio moral, sexual ou qualquer conduta que cause constrangimento.'),
]

# mapa das respostas corretas — chave é nome lógico do campo
CORRECT_ANSWERS = {
    'questao1': 'B',
    'questao2': 'C',
    'questao3': 'C',
}

class QuestionarioIntegracaoForm(forms.Form):
    questao1 = forms.ChoiceField(
        choices=Q1_CHOICES,
        widget=forms.RadioSelect,
        label="Quais cuidados são obrigatórios ao circular nas dependência da empresa?"
    )
    questao2 = forms.ChoiceField(
        choices=Q2_CHOICES,
        widget=forms.RadioSelect,
        label="O que deve ser feito ao soar o segundo alarme em caso de princípio de incêndio?"
    )
    questao3 = forms.ChoiceField(
        choices=Q3_CHOICES,
        widget=forms.RadioSelect,
        label="Qual comportamento não é tolerado no ambiente de trabalho?"
    )
