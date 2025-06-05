from django import forms
from .models import ControleChaves, Chave, Ocorrencia, Colaborador, Fornecedor, EntradaFornecedor, EntradaFornecedorAvulso
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
        fields = ['base', 'matricula', 'colaborador', 'departamento', 'chave']
        widgets = {
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'colaborador': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        matricula = cleaned_data.get("matricula")
        colaborador = cleaned_data.get("colaborador")
        departamento = cleaned_data.get("departamento")
        chave = cleaned_data.get("chave")

        if matricula and (not colaborador or not departamento):
            raise ValidationError("Matrícula inválida. Os dados do colaborador não foram preenchidos.")

        # Verificar se a chave já está em uso (com situação = RETIRADO)
        if chave:
            chave_em_uso = ControleChaves.objects.filter(chave=chave, situacao="RETIRADO").exists()
            if chave_em_uso:
                raise ValidationError(f"A chave '{chave.nome}' está atualmente indisponível.")


class OcorrenciaForm(forms.ModelForm):
    base = forms.ChoiceField(choices=BASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Ocorrencia
        fields = ['base', 'tipo', 'ocorrencia']
        widgets = {
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'ocorrencia': forms.Textarea(attrs={'class': 'form-control'}),
        }

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['cpf', 'nome', 'validade_meses']
        widgets = {
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'validade_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class EntradaFornecedorForm(forms.ModelForm):
    
    base = forms.ChoiceField(choices=BASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = EntradaFornecedor
        # Campos que o usuário irá preencher (os automáticos ficam de fora)
        fields = [
            'base',
            'fornecedor',
            'quantidade',
            'visitantes',
            'tipo_documento',
            'documento',
            'setor',
            'responsavel',
            'assinatura_portaria',
        ]
        widgets = {
            'base': forms.TextInput(attrs={'class': 'form-control'}),
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'visitantes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_documento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'documento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'setor': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'assinatura_portaria': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra fornecedores apenas com status "Integrado"
        self.fields['fornecedor'].queryset = Fornecedor.objects.filter(status='Integrado')

class EntradaFornecedorAvulsoForm(forms.ModelForm):

    base = forms.ChoiceField(
        choices=BASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = EntradaFornecedorAvulso
        fields = [
            'base',
            'fornecedor_nome',
            'cpf_ou_cnpj',
            'quantidade',
            'visitantes',
            'tipo_documento',
            'documento',
            'setor',
            'responsavel',
            'assinatura_portaria',
        ]
        widgets = {
            'fornecedor_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_ou_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'visitantes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_documento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'documento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'setor': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'assinatura_portaria': forms.TextInput(attrs={'class': 'form-control'}),
        }
