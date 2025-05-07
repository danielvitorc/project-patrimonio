from django import forms
from .models import ControleChaves, Ocorrencia, Colaborador, Fornecedor
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
    base = forms.ChoiceField(choices=BASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ControleChaves
        fields = ['base', 'matricula', 'colaborador', 'departamento']
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

        if matricula and (not colaborador or not departamento):
            raise ValidationError("Matrícula inválida. Os dados do colaborador não foram preenchidos.")


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
        fields = ['cnpj', 'nome', 'validade_meses']
        widgets = {
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'validade_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }