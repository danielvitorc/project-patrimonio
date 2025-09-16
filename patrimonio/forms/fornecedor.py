from django import forms
from django_select2.forms import Select2Widget 
from patrimonio.models import Fornecedor, Visitante, FornecedorServico, Entrega, EntradaFornecedor
from ._choices import BASE_CHOICES

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['categoria', 'validade_meses']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'validade_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

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

class FornecedorServicoForm(forms.ModelForm):
    # Campo para captura de foto via webcam
    foto_webcam = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="Foto capturada via webcam"
    )

    class Meta:
        model = FornecedorServico
        exclude = ['fornecedor']
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'atividade_servico': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_fornecedor': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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

# ESTA É A ÚNICA VERSÃO QUE DEVE EXISTIR DESTE FORMULÁRIO
class EntradaFornecedorForm(forms.ModelForm):
    base = forms.ChoiceField(
        choices=BASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Pega o queryset ordenado que a view passou
        queryset_ordenado = kwargs.pop('queryset', None)
        super().__init__(*args, **kwargs)

        # Usa o queryset ordenado, se disponível
        if queryset_ordenado is not None:
            self.fields['fornecedor'].queryset = queryset_ordenado

        # Define como o texto de cada opção será exibido
        self.fields['fornecedor'].label_from_instance = self.label_fornecedor

    def label_fornecedor(self, obj):
        # Esta função está perfeita.
        if hasattr(obj, 'visitante') and obj.visitante:
            return f"Visitante: {obj.visitante.nome}"
        elif hasattr(obj, 'fornecedor_servico') and obj.fornecedor_servico:
            return f"Fornecedor: {obj.fornecedor_servico.nome_representante}"
        elif hasattr(obj, 'entrega') and obj.entrega:
            return f"Entrega: {obj.entrega.nome_entregador}"
        return f"Fornecedor ID {obj.id}"

    class Meta:
        model = EntradaFornecedor
        fields = ['base', 'fornecedor', 'assinatura_portaria', 'setor_destino', 'responsavel_autorizante', 'modelo_veiculo', 'placa_veiculo']
        widgets = {
            # AQUI ESTÁ A VERSÃO COMPLETA E CORRIGIDA DO WIDGET:
            'fornecedor': Select2Widget(attrs={
                'class': 'form-control',  # Adiciona a classe do Bootstrap para o tamanho correto
                'data-theme': 'bootstrap-5', # Aplica o tema do Bootstrap 5 que você já importou
                'data-dropdown-parent': '#entradafornecedorModal' # Resolve o problema de foco do modal
            }),
            
            # Outros widgets
            'assinatura_portaria': forms.TextInput(attrs={'class': 'form-control'}),
            'setor_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_autorizante': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'placa_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
        }