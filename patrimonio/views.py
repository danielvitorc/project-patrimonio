from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import pandas as pd
from .forms import OcorrenciaForm,ControleChavesForm, UploadFileForm, FornecedorForm, EntradaFornecedorForm, CrachaForm, DevolucaoChaveForm, FornecedorServicoForm, Fornecedor, EntradaFornecedor, VisitanteForm, EntregaForm
from .models import Ocorrencia, ControleChaves, Colaborador, Fornecedor, EntradaFornecedor, EsquecimentoCRACHA
from datetime import date
from django.utils import timezone
from utils.email_alertas import enviar_alerta_vencimentos



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
def excluir_chave(request, chave_id):
    chave = get_object_or_404(ControleChaves, id=chave_id)
    if request.method == 'POST':
        chave.delete()
        messages.success(request, "Registro excluído com sucesso.")
        return redirect('entrega_de_chave')

@login_required
def entrega_de_chave(request):
    chaves = ControleChaves.objects.all().order_by('-id')
    form_chave = ControleChavesForm()
    devolucao_forms = {}

    # Processar entrega de chave
    if request.method == 'POST' and 'form_tipo' in request.POST and request.POST['form_tipo'] == 'entrega':
        form_chave = ControleChavesForm(request.POST, request.FILES)
        if form_chave.is_valid():
            controle = form_chave.save(commit=False)
            controle.situacao = "RETIRADO"
            controle.save()
            messages.success(request, "Entrega registrada com sucesso!")
            return redirect('entrega_de_chave')
        else:
            for erro in form_chave.non_field_errors():
                messages.error(request, erro)

    # Processar devolução
    elif request.method == 'POST' and 'form_tipo' in request.POST and request.POST['form_tipo'] == 'devolucao':
        chave_id = request.POST.get('chave_id')
        chave = get_object_or_404(ControleChaves, id=chave_id)
        form_devolucao = DevolucaoChaveForm(request.POST, request.FILES, instance=chave)
        if form_devolucao.is_valid():
            devolucao = form_devolucao.save(commit=False)
            devolucao.data_devolucao = timezone.now()
            devolucao.situacao = "DEVOLVIDO"
            devolucao.save()
            messages.success(request, "Chave devolvida com sucesso!")
            return redirect('entrega_de_chave')
        else:
            messages.error(request, "Erro ao registrar devolução.")

    # Pré-preencher formulários de devolução por chave
    for chave in chaves:
        if chave.situacao == "RETIRADO":
            devolucao_forms[chave.id] = DevolucaoChaveForm(instance=chave)

    return render(request, 'patrimonio/entrega_de_chave.html', {
        'form_chave': form_chave,
        'devolucao_forms': devolucao_forms,
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

# Função para excluir movimentação de chave
def excluir_chave(request, id):
    chave = get_object_or_404(ControleChaves, id=id)
    try:
        chave.delete()
        messages.success(request, "Movimentação de Chave excluído com sucesso.")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao tentar excluir movimentação de chave: {e}")
    return redirect('entrega_de_chave')  # Redirecionando para a view unificada

def excluir_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    fornecedor.delete()
    return redirect('patrimonio/entrada_saida_visitantes.htmla')  # ajuste conforme sua lógica


@login_required
def controle_visitantes(request):
    hoje = timezone.now().date()

    # Atualiza status automaticamente
    Fornecedor.objects.filter(data_validade__lte=hoje, status='Integrado').update(status='Pendente')

    # Envia alerta por e-mail
    enviar_alerta_vencimentos()

    form_fornecedor = FornecedorForm()
    form_visitante = VisitanteForm()
    form_fornecedor_servico = FornecedorServicoForm()
    form_entrega = EntregaForm()
    form_entrada = EntradaFornecedorForm()

    if request.method == 'POST':
        # Novo Fornecedor
        if 'submit_novo_fornecedor' in request.POST:
            form_fornecedor = FornecedorForm(request.POST)
            categoria = request.POST.get('categoria')

            form_visitante = VisitanteForm(request.POST, request.FILES) if categoria == 'VISITANTE' else VisitanteForm()
            form_fornecedor_servico = FornecedorServicoForm(request.POST, request.FILES) if categoria == 'FORNECEDOR' else FornecedorServicoForm()
            form_entrega = EntregaForm(request.POST, request.FILES) if categoria == 'ENTREGA' else EntregaForm()

            if form_fornecedor.is_valid():
                fornecedor = form_fornecedor.save(commit=False)
                fornecedor.save()

                if categoria == 'VISITANTE' and form_visitante.is_valid():
                    visitante = form_visitante.save(commit=False)
                    visitante.fornecedor = fornecedor
                    visitante.save()

                elif categoria == 'FORNECEDOR' and form_fornecedor_servico.is_valid():
                    servico = form_fornecedor_servico.save(commit=False)
                    servico.fornecedor = fornecedor
                    servico.save()

                elif categoria == 'ENTREGA' and form_entrega.is_valid():
                    entrega = form_entrega.save(commit=False)
                    entrega.fornecedor = fornecedor
                    entrega.save()

                return redirect('controle_visitantes')

        # Entrada
        elif 'submit_entrada' in request.POST:
            form_entrada = EntradaFornecedorForm(request.POST)
            if form_entrada.is_valid():
                entrada = form_entrada.save(commit=False)
                entrada.status = 'Em andamento'
                entrada.usuario_registro = request.user
                entrada.save()
                return redirect('controle_visitantes')

        # Marcar saída
        elif 'submit_saida' in request.POST:
            entrada_id = request.POST.get('entrada_id')
            entrada = get_object_or_404(EntradaFornecedor, id=entrada_id)
            entrada.status = 'Saiu'
            entrada.save()
            return redirect('controle_visitantes')

    fornecedores = Fornecedor.objects.all()
    entradas = EntradaFornecedor.objects.all().order_by('-data', '-horario_entrada')

    context = {
        'form_fornecedor': form_fornecedor,
        'form_visitante': form_visitante,
        'form_fornecedor_servico': form_fornecedor_servico,
        'form_entrega': form_entrega,
        'form_entrada': form_entrada,
        'fornecedores': fornecedores,
        'entradas': entradas,
    }
    return render(request, 'patrimonio/entrada_saida_visitantes.html', context)

@login_required
def status_fornecedor(request, pk):
    entrada = get_object_or_404(EntradaFornecedor, pk=pk)
    entrada.status = "Saiu"
    entrada.save()
    return redirect('controle_visitantes')



def detalhes_entrada(request, entrada_id):
    entrada = get_object_or_404(EntradaFornecedor, pk=entrada_id)
    return render(request, 'patrimonio/detalhes_entrada.html', {'entrada': entrada})

def excluir_entrada(request, pk):
    entrada = get_object_or_404(EntradaFornecedor, pk=pk)
    if request.method == "POST":
        entrada.delete()
        return redirect('controle_visitantes')  # redirecione para onde achar adequado
    return render(request, '/confirmar_exclusao.html', {'entrada': entrada})


def fornecedores_cadastrados_view(request):
    fornecedores = Fornecedor.objects.all().order_by('-data_integracao')
    return render(request, 'patrimonio/fornecedores_cadastrados.html', {'fornecedores': fornecedores})