from django import forms
from django.core.exceptions import ValidationError
from patrimonio.models import EsquecimentoCRACHA

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