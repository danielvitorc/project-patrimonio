from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from patrimonio.forms import UploadFileForm
from patrimonio.models import Colaborador
import pandas as pd

@login_required
def home(request):
    if request.method == 'POST':
        form_colaborador = UploadFileForm(request.POST, request.FILES)
        if form_colaborador.is_valid():
            file = request.FILES['file']
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith(('.xls','.xlsx')):
                    df = pd.read_excel(file)
                else:
                    return HttpResponse("Formato de arquivo não suportado.", status=400)
                
                df.columns = df.columns.str.strip().str.lower()
                required_columns = [
                        "matricula", "nome", "departamento", 
                    ]
                if not all(col in df.columns for col in required_columns):
                    return HttpResponse("A planilha de colaborador deve conter todas as colunas necessárias.", status=400)
                
                colaboradores = [
                    Colaborador(
                        matricula=row['matricula'],
                        nome=row['nome'],
                        departamento=row['departamento'],

                        )
                    for _, row in df.iterrows()
                ]
                Colaborador.objects.bulk_create(colaboradores)
                return redirect('home')

            except Exception as e:
                return HttpResponse(f"Erro ao processar o arquivo: {str(e)}", status=500)
    else:
        form_colaborador = UploadFileForm()

    
    return render(request, 'patrimonio/home.html', {
        'form_colaborador': form_colaborador,
    })