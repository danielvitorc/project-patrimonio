from django import forms
from django.core.exceptions import ValidationError
from patrimonio.models import ControleChaves, Chave
from ._choices import BASE_CHOICES

class DevolucaoChaveForm(forms.ModelForm):
    class Meta:
        model = ControleChaves
        fields = ['matricula_devolveu', 'colaborador_devolveu', 'foto_devolucao']
        widgets = {
            'matricula_devolveu': forms.TextInput(attrs={'class': 'form-control'}),
            'colaborador_devolveu': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_devolucao': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        matricula_devolveu = cleaned_data.get("matricula_devolveu")
        colaborador_devolveu = cleaned_data.get("colaborador_devolveu")

        # Validação CORRIGIDA: Verifica apenas se, após digitar a matrícula,
        # o nome do colaborador foi preenchido (pelo JavaScript ou manualmente).
        if matricula_devolveu and not colaborador_devolveu:
            raise ValidationError("Matrícula inválida ou não encontrada. O nome do colaborador não foi preenchido.")
            
        # Você também pode adicionar uma validação para garantir que a matrícula foi preenchida
        if not matricula_devolveu:
            raise ValidationError("O campo Matrícula é obrigatório.")

        return cleaned_data


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
        fields = ['base', 'matricula_recebendo', 'colaborador_recebendo', 'departamento', 'chave', 'foto_entrega']
        widgets = {
            'base': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula_recebendo': forms.TextInput(attrs={'class': 'form-control'}),
            'colaborador_recebendo': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'chave': forms.Select(attrs={'class': 'form-control'}),
            'foto_entrega': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


    def clean(self):
        cleaned_data = super().clean()
        matricula_recebendo = cleaned_data.get("matricula_recebendo")
        colaborador_recebendo = cleaned_data.get("colaborador_recebendo")
        departamento = cleaned_data.get("departamento")
        chave = cleaned_data.get("chave")

        if matricula_recebendo and (not colaborador_recebendo or not departamento):
            raise ValidationError("Matrícula inválida. Os dados do colaborador que entregou não foram preenchidos.")

        # Verificar se a chave já está em uso (com situação = RETIRADO)
        if chave:
            chave_em_uso = ControleChaves.objects.filter(chave=chave, situacao="RETIRADO").exists()
            if chave_em_uso:
                raise ValidationError(f"A chave '{chave.nome}' está atualmente indisponível.")