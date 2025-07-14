from django import forms
from .models import ControleChaves, Chave, Ocorrencia, Colaborador, Fornecedor, Visitante, FornecedorServico, Entrega, EntradaFornecedor, EsquecimentoCRACHA
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):
    file = forms.FileField()

BASE_CHOICES = [
    ('BASE TARUMÃ', 'BASE TARUMÃ'),
    ('BASE FLORES', 'BASE FLORES'),
    ('BASE PONTA NEGRA', 'BASE PONTA NEGRA'),
    ('BASE SÃO JOSÉ', 'BASE SÃO JOSÉ'),
    ('BASE CIDADE NOVA', 'BASE CIDADE NOVA')
]

class DevolucaoChaveForm(forms.ModelForm):
    class Meta:
        model = ControleChaves
        fields = ['matricula_recebeu', 'colaborador_recebeu', 'foto_devolucao']
        widgets = {
            'matricula_recebeu': forms.TextInput(attrs={'class': 'form-control'}),
            'colaborador_recebeu': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_devolucao': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        matricula_entregou = cleaned_data.get("matricula_entregou")
        colaborador_entregou = cleaned_data.get("colaborador_entregou")
        departamento = cleaned_data.get("departamento")

        if matricula_entregou and (not colaborador_entregou or not departamento):
            raise ValidationError("Matrícula inválida. Os dados do colaborador que entregou não foram preenchidos.")
class ControleChavesForm(forms.ModelForm):
    base = forms.ChoiceField(
        choices=BASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    chave = forms.ModelChoiceField(
        queryset=Chave.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ControleChaves
        fields = ['base', 'matricula_entregou', 'colaborador_entregou', 'departamento', 'chave', 'foto_entrega']
        widgets = {
            'base': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula_entregou': forms.TextInput(attrs={'class': 'form-control'}),
            'colaborador_entregou': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'chave': forms.Select(attrs={'class': 'form-control'}),
            'foto_entrega': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


    def clean(self):
        cleaned_data = super().clean()
        matricula_entregou = cleaned_data.get("matricula_entregou")
        colaborador_entregou = cleaned_data.get("colaborador_entregou")
        departamento = cleaned_data.get("departamento")
        chave = cleaned_data.get("chave")

        if matricula_entregou and (not colaborador_entregou or not departamento):
            raise ValidationError("Matrícula inválida. Os dados do colaborador que entregou não foram preenchidos.")

        # Verificar se a chave já está em uso (com situação = RETIRADO)
        if chave:
            chave_em_uso = ControleChaves.objects.filter(chave=chave, situacao="RETIRADO").exists()
            if chave_em_uso:
                raise ValidationError(f"A chave '{chave.nome}' está atualmente indisponível.")

class CrachaForm(forms.ModelForm):
    class Meta:
        model = EsquecimentoCRACHA
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        matricula = cleaned_data.get("matricula")
        colaborador = cleaned_data.get("colaborador")
        departamento = cleaned_data.get("departamento")

        if matricula and (not colaborador or not departamento):
            raise ValidationError("Matrícula inválida. Os dados do colaborador não foram preenchidos.")
        
class OcorrenciaForm(forms.ModelForm):
    base = forms.ChoiceField(choices=BASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Ocorrencia
        fields = ['base', 'ocorrencia']
        widgets = {
            'ocorrencia': forms.Textarea(attrs={'class': 'form-control'}),
        }



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



class EntradaFornecedorForm(forms.ModelForm):
    base = forms.ChoiceField(
        choices=BASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza o texto de cada fornecedor no dropdown
        self.fields['fornecedor'].label_from_instance = self.label_fornecedor

    def label_fornecedor(self, obj):
        if hasattr(obj, 'visitante'):
            return f"Visitante: {obj.visitante.nome}"
        elif hasattr(obj, 'fornecedor_servico'):
            return f"Fornecedor: {obj.fornecedor_servico.nome_representante}"
        elif hasattr(obj, 'entrega'):
            return f"Entrega: {obj.entrega.nome_entregador}"
        return f"Fornecedor ID {obj.id}"

    class Meta:
        model = EntradaFornecedor
        fields = ['base', 'fornecedor', 'assinatura_portaria', 'setor_destino', 'responsavel_autorizante', 'modelo_veiculo', 'placa_veiculo']
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
            'assinatura_portaria': forms.TextInput(attrs={'class': 'form-control'}),
            'setor_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_autorizante': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'placa_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
        }
