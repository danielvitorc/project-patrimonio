from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import pandas as pd
from .forms import OcorrenciaForm,ControleChavesForm, UploadFileForm, FornecedorForm, EntradaFornecedorForm
from .models import Ocorrencia, ControleChaves, Colaborador, Fornecedor, EntradaFornecedor
from datetime import date

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

def buscar_colaborador_por_matricula(request):
    matricula = request.GET.get('matricula')
    try:
        colaborador = Colaborador.objects.get(matricula=matricula)
        return JsonResponse({
            'nome': colaborador.nome,
            'departamento': colaborador.departamento
        })
    except Colaborador.DoesNotExist:
        return JsonResponse({'erro': 'Colaborador não encontrado'}, status=404)
    

@login_required
def devolver_chave(request, pk):
    chave = get_object_or_404(ControleChaves, pk=pk)
    chave.situacao = "DEVOLVIDO"
    chave.save()
    return redirect('entrega_de_chave')
@login_required
def controle_visitantes(request):
    
    hoje = date.today()

    fornecedores_vencidos = Fornecedor.objects.filter(data_validade__lte =hoje, status='Integrado')
    for fornecedor in fornecedores_vencidos:
        fornecedor.status = 'Pendente'
        fornecedor.save(update_fields=['status'])

    # Processa formulário de Fornecedor
    if request.method == 'POST' and 'submit_fornecedor' in request.POST:
        form_fornecedor = FornecedorForm(request.POST)
        form_entrada = EntradaFornecedorForm()
        if form_fornecedor.is_valid():
            form_fornecedor.save()
            return redirect('controle_visitantes')

    # Processa formulário de EntradaFornecedor
    elif request.method == 'POST' and 'submit_entrada' in request.POST:
        form_entrada = EntradaFornecedorForm(request.POST)
        form_fornecedor = FornecedorForm()
        if form_entrada.is_valid():
            entrada = form_entrada.save(commit=False)
            entrada.status = 'Em andamento'  # status default
            entrada.save()
            return redirect('controle_visitantes')

    else:
        form_fornecedor = FornecedorForm()
        form_entrada = EntradaFornecedorForm()

    fornecedores = Fornecedor.objects.all()
    entradas = EntradaFornecedor.objects.all().order_by('-data', '-horario_entrada')

    return render(request, 'patrimonio/entrada_saida_visitantes.html', {
        'form_fornecedor': form_fornecedor, 
        'form_entrada': form_entrada,
        'fornecedores': fornecedores,
        'entradas': entradas,
        })


@login_required
def status_fornecedor(request, pk):
    entrada = get_object_or_404(EntradaFornecedor, pk=pk)
    entrada.status = "Saiu"
    entrada.save()
    return redirect('controle_visitantes')