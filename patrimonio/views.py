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
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
import base64
from django.core.files.base import ContentFile



# ===== Tela de Login ===== 
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Verificar se o usuário tem perfil
            if not hasattr(user, 'profile'):
                from .models import UserProfile
                UserProfile.objects.create(user=user)
            
            # Verificar se o usuário está bloqueado
            if user.profile.is_blocked:
                messages.error(request, 'Sua conta está bloqueada. Entre em contato com o administrador.')
                return render(request, 'patrimonio/login.html')
            
            login(request, user)
            
            # Redirecionar para tela de admin se for administrador
            if user.profile.is_admin:
                return redirect('admin_dashboard')
            else:
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

def process_webcam_photo(photo_data, field_name):
    """
    Processa a foto capturada via webcam e retorna um arquivo Django
    """
    if photo_data and photo_data.startswith('data:image'):
        # Remove o prefixo data:image/jpeg;base64,
        format, imgstr = photo_data.split(';base64,')
        ext = format.split('/')[-1]
        
        # Decodifica o base64
        img_data = base64.b64decode(imgstr)
        
        # Cria um arquivo Django
        img_file = ContentFile(img_data, name=f'{field_name}.{ext}')
        return img_file
    return None



def enviar_alerta_vencimentos():
    """
    Função para enviar alertas de vencimento (implementar conforme necessário)
    """
    # Implementar lógica de envio de e-mail aqui
    pass


def excluir_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    fornecedor.delete()
    return redirect('controle_visitantes')  # Corrigido o redirect

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
                    
                    foto_base64 = request.POST.get('foto_visitante')
                    if foto_base64:
                        img_file = process_webcam_photo(foto_base64, 'visitante')
                        if img_file:
                            visitante.foto_visitante = img_file
                    
                    visitante.save()
                    
                elif categoria == 'FORNECEDOR' and form_fornecedor_servico.is_valid():
                    servico = form_fornecedor_servico.save(commit=False)
                    servico.fornecedor = fornecedor

                    # Processa foto da webcam se disponível
                    foto_base64 = request.POST.get('foto_webcam')  # Corrigido aqui
                    if foto_base64:
                        img_file = process_webcam_photo(foto_base64, 'fornecedor')
                        if img_file:
                            servico.foto_fornecedor = img_file

                    servico.save()

                elif categoria == 'ENTREGA' and form_entrega.is_valid():
                    entrega = form_entrega.save(commit=False)
                    entrega.fornecedor = fornecedor
                    
                    # Processa foto da webcam se disponível
                    foto_webcam = request.POST.get('foto_webcam')
                    if foto_webcam:
                        img_file = process_webcam_photo(foto_webcam, 'entrega')
                        if img_file:
                            entrega.foto_caixa_entrega = img_file
                    
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


def fornecedores_cadastrados(request):
    fornecedores = Fornecedor.objects.all().order_by('-data_integracao')
    return render(request, 'patrimonio/fornecedores_cadastrados.html', {'fornecedores': fornecedores})

def modal_editar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)

    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)

        if fornecedor.categoria == 'VISITANTE':
            form_sub = VisitanteForm(request.POST, request.FILES, instance=fornecedor.visitante)
        elif fornecedor.categoria == 'FORNECEDOR':
            form_sub = FornecedorServicoForm(request.POST, request.FILES, instance=fornecedor.fornecedor_servico)
        elif fornecedor.categoria == 'ENTREGA':
            form_sub = EntregaForm(request.POST, request.FILES, instance=fornecedor.entrega)
        else:
            form_sub = None

        if form.is_valid() and (not form_sub or form_sub.is_valid()):
            form.save()
            if form_sub:
                form_sub.save()
            return JsonResponse({'success': True})

        form_html = render_to_string('patrimonio/includes/form_editar_fornecedor.html', {
            'form': form,
            'form_sub': form_sub,
            'fornecedor': fornecedor,
        }, request=request)
        return JsonResponse({'success': False, 'form_html': form_html})

    else:
        form = FornecedorForm(instance=fornecedor)
        if fornecedor.categoria == 'VISITANTE':
            form_sub = VisitanteForm(instance=fornecedor.visitante)
        elif fornecedor.categoria == 'FORNECEDOR':
            form_sub = FornecedorServicoForm(instance=fornecedor.fornecedor_servico)
        elif fornecedor.categoria == 'ENTREGA':
            form_sub = EntregaForm(instance=fornecedor.entrega)
        else:
            form_sub = None

        form_html = render_to_string('patrimonio/includes/form_editar_fornecedor.html', {
            'form': form,
            'form_sub': form_sub,
            'fornecedor': fornecedor,
        }, request=request)

        return JsonResponse({'form_html': form_html})
    
def excluir_fornecedor(request, pk):
    if request.method == 'POST':
        fornecedor = get_object_or_404(Fornecedor, pk=pk)
        fornecedor.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

# ===== Views de Administração =====

from django.contrib.auth.models import User
from .models import UserProfile, ActivityLog
from django.contrib.auth.forms import UserCreationForm
from django import forms

def log_activity(user, action):
    ActivityLog.objects.create(user=user, action=action)

# Decorator para verificar se o usuário é admin
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'Acesso negado. Você não tem permissão de administrador.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard(request):
    """Dashboard principal do administrador"""
    total_usuarios = User.objects.count()
    usuarios_bloqueados = UserProfile.objects.filter(is_blocked=True).count()
    usuarios_admin = UserProfile.objects.filter(is_admin=True).count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    
    # Resumo de Atividades
    atividades_recentes = ActivityLog.objects.all().order_by("-timestamp")[:10] # Últimas 10 atividades
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_bloqueados': usuarios_bloqueados,
        'usuarios_admin': usuarios_admin,
        'usuarios_ativos': usuarios_ativos,
        'atividades_recentes': atividades_recentes,
    }
    return render(request, 'patrimonio/admin/dashboard.html', context)

@admin_required
def admin_usuarios(request):
    """Lista todos os usuários para gerenciamento"""
    usuarios = User.objects.all().order_by('username')
    return render(request, 'patrimonio/admin/usuarios.html', {'usuarios': usuarios})

class AdminUserCreationForm(UserCreationForm):
    """Formulário customizado para criação de usuários pelo admin"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    is_admin = forms.BooleanField(required=False, label='É Administrador')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

@admin_required
def admin_criar_usuario(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Criar ou atualizar perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_admin = form.cleaned_data.get('is_admin', False)
            profile.save()
            
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            log_activity(request.user, f'Criou o usuário {user.username}')
            return redirect('admin_usuarios')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'patrimonio/admin/criar_usuario.html', {'form': form})

@admin_required
def admin_editar_usuario(request, user_id):
    """Editar usuário existente"""
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Atualizar dados básicos
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name = request.POST.get('last_name', '')
        usuario.email = request.POST.get('email', '')
        usuario.is_active = 'is_active' in request.POST
        usuario.save()
        
        # Atualizar perfil
        profile, created = UserProfile.objects.get_or_create(user=usuario)
        profile.is_admin = 'is_admin' in request.POST
        profile.is_blocked = 'is_blocked' in request.POST
        profile.save()
        
        messages.success(request, f'Usuário {usuario.username} atualizado com sucesso!')
        log_activity(request.user, f'Atualizou o usuário {usuario.username}')
        return redirect('admin_usuarios')
    
    return render(request, 'patrimonio/admin/editar_usuario.html', {'usuario': usuario})

@admin_required
def admin_trocar_senha(request, user_id):
    """Trocar senha de um usuário"""
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if nova_senha and nova_senha == confirmar_senha:
            if len(nova_senha) >= 8:
                usuario.set_password(nova_senha)
                usuario.save()
                messages.success(request, f'Senha do usuário {usuario.username} alterada com sucesso!')
                log_activity(request.user, f'Alterou a senha do usuário {usuario.username}')
                return redirect('admin_usuarios')
            else:
                messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
        else:
            messages.error(request, 'As senhas não coincidem.')
    
    return render(request, 'patrimonio/admin/trocar_senha.html', {'usuario': usuario})

@admin_required
def admin_bloquear_usuario(request, user_id):
    """Bloquear/desbloquear usuário"""
    usuario = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=usuario)
    
    # Não permitir que o admin se bloqueie
    if usuario == request.user:
        messages.error(request, 'Você não pode bloquear sua própria conta.')
        return redirect('admin_usuarios')
    
    profile.is_blocked = not profile.is_blocked
    profile.save()
    
    status = 'bloqueado' if profile.is_blocked else 'desbloqueado'
    messages.success(request, f'Usuário {usuario.username} {status} com sucesso!')
    log_activity(request.user, f'{status.capitalize()} o usuário {usuario.username}')
    return redirect('admin_usuarios')

@admin_required
def admin_excluir_usuario(request, user_id):
    """Excluir usuário"""
    usuario = get_object_or_404(User, id=user_id)
    
    # Não permitir que o admin se exclua
    if usuario == request.user:
        messages.error(request, 'Você não pode excluir sua própria conta.')
        return redirect('admin_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuário {username} excluído com sucesso!')
        log_activity(request.user, f'Excluiu o usuário {username}')
        return redirect('admin_usuarios')
    
    return render(request, 'patrimonio/admin/confirmar_exclusao.html', {'usuario': usuario})


def exportar_fornecedores_excel(request, categoria=None):
    """
    View para exportar fornecedores para Excel, com filtro opcional por categoria.
    """
    fornecedores = Fornecedor.objects.select_related(
        'visitante', 'fornecedor_servico', 'entrega'
    ).all().order_by('-data_integracao')

    if categoria:
        fornecedores = fornecedores.filter(categoria=categoria.upper())

    dados_exportacao = []

    for fornecedor in fornecedores:
        linha = {
            'ID': fornecedor.id,
            'Categoria': fornecedor.get_categoria_display(),
            'Data de Integração': fornecedor.data_integracao.strftime('%d/%m/%Y'),
            'Data de Validade': fornecedor.data_validade.strftime('%d/%m/%Y'),
            'Validade (Meses)': fornecedor.validade_meses,
            'Status': fornecedor.status,
        }

        if fornecedor.categoria == 'VISITANTE' and hasattr(fornecedor, 'visitante'):
            visitante = fornecedor.visitante
            linha.update({
                'Nome/Empresa': visitante.nome,
                'Documento': visitante.documento,
                'Motivo da Visita': visitante.motivo_visita,
                'Representante': '',
                'Atividade/Serviço': '',
            })
        elif fornecedor.categoria == 'FORNECEDOR' and hasattr(fornecedor, 'fornecedor_servico'):
            servico = fornecedor.fornecedor_servico
            linha.update({
                'Nome/Empresa': servico.nome_empresa,
                'Documento': servico.documento,
                'Motivo da Visita': '',
                'Representante': servico.nome_representante,
                'Atividade/Serviço': servico.atividade_servico,
            })
        else:
            linha.update({
                'Nome/Empresa': '',
                'Documento': '',
                'Motivo da Visita': '',
                'Representante': '',
                'Atividade/Serviço': '',
            })

        dados_exportacao.append(linha)

    df = pd.DataFrame(dados_exportacao)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    filename = 'fornecedores_cadastrados.xlsx'
    if categoria:
        filename = f'{categoria.lower()}_cadastrados.xlsx'

    response['Content-Disposition'] = f'attachment; filename={filename}'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Fornecedores', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Fornecedores']

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        worksheet.set_column('A:A', 8)   # ID
        worksheet.set_column('B:B', 15)  # Categoria
        worksheet.set_column('C:C', 30)  # Nome/Empresa
        worksheet.set_column('D:D', 15)  # Data Integração
        worksheet.set_column('E:E', 15)  # Data Validade
        worksheet.set_column('F:F', 12)  # Validade Meses
        worksheet.set_column('G:G', 12)  # Status
        worksheet.set_column('H:H', 20)  # Documento
        worksheet.set_column('I:I', 25)  # Motivo da Visita
        worksheet.set_column('J:J', 25)  # Representante
        worksheet.set_column('K:K', 25)  # Atividade/Serviço

    return response

def exportar_fornecedores_servico_excel(request):
    return exportar_fornecedores_excel(request, categoria='FORNECEDOR')

def exportar_visitantes_excel(request):
    return exportar_fornecedores_excel(request, categoria='VISITANTE')
