from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from patrimonio.forms import CrachaForm
from patrimonio.models import EsquecimentoCRACHA
import pandas as pd

@login_required
def ocorrencia_cracha(request):
    if request.method == 'POST':
        form_cracha = CrachaForm(request.POST)
        if form_cracha.is_valid():
            form_cracha.save()
            return redirect('ocorrencia_cracha')  # redireciona para a mesma view
    else:
        form_cracha = CrachaForm()

    registros = EsquecimentoCRACHA.objects.all().order_by('-data')

    return render(request, 'patrimonio/ocorrencia_cracha.html', {
        'form_cracha': form_cracha,
        'registros': registros
    })

@login_required
def exportar_ocorrencias_excel(request):
    registros = EsquecimentoCRACHA.objects.all().values(
        'matricula', 'colaborador', 'departamento', 'data', 'motivo'
    )

    df = pd.DataFrame(list(registros))
    df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y')

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=ocorrencias_cracha.xlsx'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Ocorrencias', index=False)

    return response