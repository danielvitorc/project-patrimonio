from django import forms
from .models import ControleChaves, Ocorrencia

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

class OcorrenciaForm(forms.ModelForm):
    base = forms.ChoiceField(choices=BASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Ocorrencia
        fields = ['base', 'tipo', 'ocorrencia']
        widgets = {
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'ocorrencia': forms.Textarea(attrs={'class': 'form-control'}),
        }
