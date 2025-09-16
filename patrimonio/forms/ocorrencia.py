from django import forms
from patrimonio.models import Ocorrencia
from ._choices import BASE_CHOICES

class OcorrenciaForm(forms.ModelForm):
    base = forms.ChoiceField(choices=BASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Ocorrencia
        fields = ['base', 'ocorrencia']
        widgets = {
            'ocorrencia': forms.Textarea(attrs={'class': 'form-control'}),
        }