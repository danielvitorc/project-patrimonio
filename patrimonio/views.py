from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import pandas as pd
from .forms import OcorrenciaForm,ControleChavesForm, UploadFileForm
from .models import Ocorrencia, ControleChaves, Colaborador

# ===== Tela de Login ===== 
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirecionar para a página inicial pós-login
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'patrimonio/login.html')

# ==== Função para deslogar do sistema =====
def logout_usuario(request):
    logout(request)
    return redirect('login')

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

@login_required
def livro_de_ocorrencia(request):

    ocorrencias = Ocorrencia.objects.all().order_by('-id')

    if request.method == 'POST':
        form_ocorrencia = OcorrenciaForm(request.POST)
        if form_ocorrencia.is_valid():
            ocorrencia = form_ocorrencia.save(commit=False)
            ocorrencia.usuario = request.user
            ocorrencia.save()
            return redirect('livro_de_ocorrencia')
    else:
        form_ocorrencia = OcorrenciaForm()

    return render(request, 'patrimonio/livro_de_ocorrencia.html', {
        'form_ocorrencia': form_ocorrencia, 
        'ocorrencias': ocorrencias,})

@login_required
def entrega_de_chave(request):

    chaves = ControleChaves.objects.all().order_by('-id')

    if request.method == 'POST':
        form_chave = ControleChavesForm(request.POST)
        if form_chave.is_valid():
            chave = form_chave.save(commit=False)
            chave.save()
            return redirect('entrega_de_chave')
    else:
        form_chave = ControleChavesForm()

    return render(request, 'patrimonio/entrega_de_chave.html', {
        'form_chave' : form_chave,
        'chaves': chaves,
    })
