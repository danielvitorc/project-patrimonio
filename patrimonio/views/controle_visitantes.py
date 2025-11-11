# project-patrimonio/patrimonio/views/controle_visitantes.py

from django.contrib.auth.decorators import login_required
from django.db.models import Value, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from patrimonio.forms import FornecedorForm, VisitanteForm, EntregaForm, EntradaFornecedorForm, FornecedorPrestadorForm, TrabalhadorCLTForm, PessoaJuridicaForm, MEIForm, AutonomoForm, AssociadoForm, FornecedorServicoForm, QuestionarioIntegracaoForm, CORRECT_ANSWERS
from patrimonio.models import Fornecedor,FornecedorServico, EntradaFornecedor, Integracao, IntegracaoToken, QuestionarioIntegracao
from django.views.decorators.http import require_POST
from patrimonio.utils import process_webcam_photo, enviar_alerta_vencimentos
from django.core.files.base import ContentFile
from datetime import timedelta, datetime
import secrets
import base64
import uuid
from django.core.paginator import Paginator # 1. Importar Paginator
from django.db import transaction # Importar transaction (já estava em uso abaixo)


@login_required
def controle_visitantes(request):
    hoje = timezone.now().date()

    # Atualiza status automaticamente
    Fornecedor.objects.filter(integracoes__data_validade__lte=hoje, status='Integrado').update(status='Pendente')

    # Envia alerta por e-mail
    enviar_alerta_vencimentos()

    # --- INÍCIO DA CORREÇÃO ---

    # 1. Crie o queryset de Fornecedor ordenado alfabeticamente
    fornecedores_ordenados = Fornecedor.objects.annotate(
        nome_ordenado=Coalesce(
            'visitante__nome',
            'fornecedor_servico__nome_empresa',  # CORRIGIDO AQUI
            'entrega__nome_entregador',
            Value('Sem Nome')
        )
    ).order_by('nome_ordenado')

    # 2. Instancie os formulários, passando o queryset para o form_entrada
    form_fornecedor = FornecedorForm()
    form_visitante = VisitanteForm()
    form_entrega = EntregaForm()
    
    # Passe o queryset ordenado para o formulário de entrada
    form_entrada = EntradaFornecedorForm(queryset=fornecedores_ordenados)


    if request.method == 'POST':
        # ... (Toda a lógica de POST (submit_novo_fornecedor, submit_entrada, submit_saida) permanece a mesma) ...
        # (pois todos eles redirecionam em caso de sucesso)

        # Novo Fornecedor (esta parte não precisa mudar)
        if 'submit_novo_fornecedor' in request.POST:
                    form_fornecedor = FornecedorForm(request.POST)
                    categoria = request.POST.get('categoria')

                    form_visitante = VisitanteForm(request.POST, request.FILES) if categoria == 'VISITANTE' else VisitanteForm()
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
            # Ao processar o POST, também precisamos passar o queryset
            # para que, em caso de erro de validação, o formulário
            # seja renderizado novamente com a lista ordenada.
            form_entrada = EntradaFornecedorForm(request.POST, queryset=fornecedores_ordenados)
            if form_entrada.is_valid():
                entrada = form_entrada.save(commit=False)
                entrada.status = 'Em andamento'
                entrada.usuario_registro = request.user
                entrada.save()
                return redirect('controle_visitantes')

        # Marcar saída (esta parte não precisa mudar)
        elif 'submit_saida' in request.POST:
            entrada_id = request.POST.get('entrada_id')
            entrada = get_object_or_404(EntradaFornecedor, id=entrada_id)
            entrada.status = 'Saiu'
            entrada.save()
            return redirect('controle_visitantes')
            

    # --- Fim da lógica POST, início da lógica GET ---

    fornecedores = Fornecedor.objects.select_related(
        'visitante',           # Carrega o relacionamento com Visitante
        'fornecedor_servico'   # Carrega o relacionamento com FornecedorServico
    ).all()

    # 2. Obter a lista completa de entradas
    entradas_list = EntradaFornecedor.objects.all().order_by('-data', '-horario_entrada')
    
    # 3. Aplicar paginação
    paginator = Paginator(entradas_list, 25) # 25 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'form_fornecedor': form_fornecedor,
        'form_visitante': form_visitante,
        'form_entrega': form_entrega,
        'form_entrada': form_entrada, # O form_entrada agora contém a lista ordenada
        'fornecedores': fornecedores, # Mantém a lista completa para o modal de entrada
        'entradas': page_obj,   # 4. Envia o objeto da página
        'page_obj': page_obj,   # 5. Envia o page_obj para o include 'pagination.html'
    }
    return render(request, 'patrimonio/entrada_saida_visitantes.html', context)


@login_required
def excluir_fornecedor(request, pk):
    if request.method == 'POST':
        fornecedor = get_object_or_404(Fornecedor, pk=pk)
        fornecedor.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def status_fornecedor(request, pk):
    entrada = get_object_or_404(EntradaFornecedor, pk=pk)
    entrada.status = "Saiu"
    entrada.save()
    return redirect('controle_visitantes')

# Em patrimonio/views.py

from django.db import transaction


@login_required
def fornecedores_filtrados(request):
    categoria = request.GET.get("categoria")
    status = request.GET.get("status")
    fornecedor_nome = request.GET.get("fornecedor")
    data_integracao = request.GET.get("data_integracao")

    fornecedores = Fornecedor.objects.select_related('visitante', 'fornecedor_servico').prefetch_related(
        'trabalhadores_clt', 'pessoas_juridicas', 'meis', 'autonomos', 'associados'
    ).order_by('id')

    # --- Filtros ---
    if categoria:
        fornecedores = fornecedores.filter(categoria__icontains=categoria)

    if status:
        status = status.strip().lower()
        if status == "pendente":
            fornecedores = fornecedores.filter(
                Q(status__iexact="Pendente") | Q(status__iexact="Sem integração")
            )
        else:
            fornecedores = fornecedores.filter(status__iexact=status)

    if fornecedor_nome:
        fornecedores = fornecedores.filter(
            Q(fornecedor_servico__nome_empresa__icontains=fornecedor_nome)
            | Q(trabalhadores_clt__nome_representante__icontains=fornecedor_nome)
            | Q(visitante__nome__icontains=fornecedor_nome)
        )

    if data_integracao:
        try:
            data_obj = datetime.strptime(data_integracao, "%Y-%m-%d").date()
            fornecedores = fornecedores.filter(integracoes__data_integracao=data_obj)
        except ValueError:
            pass

    # --- Paginação (como na view principal) ---
    paginator = Paginator(fornecedores, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- Contexto igual ao da view principal ---
    context = {
        "page_obj": page_obj,
        "fornecedores": page_obj,
        "fornecedor_prestador_form": FornecedorPrestadorForm(),
        "fornecedor_servico_form": FornecedorServicoForm(),
        "clt_form": TrabalhadorCLTForm(),
        "pj_form": PessoaJuridicaForm(),
        "mei_form": MEIForm(),
        "autonomo_form": AutonomoForm(),
        "associado_form": AssociadoForm(),
        "filtros": {
            "categoria": categoria or "",
            "status": status or "",
            "fornecedor": fornecedor_nome or "",
            "data_integracao": data_integracao or "",
        },
    }

    return render(request, "patrimonio/fornecedores_cadastrados.html", context)


@login_required
@require_POST
def excluir_fornecedor(request):
    # ... (view excluir_fornecedor permanece a mesma) ...
    fornecedor_id = request.POST.get("id")

    if not fornecedor_id:
        return JsonResponse({"success": False, "message": "ID não fornecido."}, status=400)

    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)
    fornecedor.delete()

    return JsonResponse({"success": True, "message": "Fornecedor excluído com sucesso!"})

@login_required
def fornecedores_cadastrados(request):
    # Limpar filtros da sessão se navegar diretamente
    if 'page' not in request.GET and 'categoria' not in request.GET:
        if 'fornecedores_filtros' in request.session:
            del request.session['fornecedores_filtros']

    # 1. Inicialize todos os formulários...
    fornecedor_form = FornecedorPrestadorForm()
    fornecedor_servico_form = FornecedorServicoForm() # Adicionado aqui para o contexto inicial
    clt_form = TrabalhadorCLTForm()
    pj_form = PessoaJuridicaForm()
    mei_form = MEIForm()
    autonomo_form = AutonomoForm()
    associado_form = AssociadoForm()

    if request.method == "POST":
        # ... (Toda a lógica de POST para criar novo fornecedor permanece a mesma) ...
        # (pois redireciona ou re-renderiza com formulários, não com a lista paginada)
        
        # Extrair dados básicos do POST
        categoria = request.POST.get("categoria")
        subcategoria_slug = request.POST.get("subcategoria")
        
        # Mapeamento dos valores do HTML para os formulários e modelos
        form_map = {
            "trabalhador_clt": (TrabalhadorCLTForm, "CLT"),
            "pessoa_juridica": (PessoaJuridicaForm, "PJ"),
            "mei": (MEIForm, "MEI"),
            "autonomo": (AutonomoForm, "AUTONOMO"),
            "associado": (AssociadoForm, "ASSOCIADO"),
        }

        trabalhador_form = None

        if categoria == "FORNECEDOR" and subcategoria_slug in form_map:
            TrabalhadorForm, subcategoria_model = form_map[subcategoria_slug]

            # 2. Instancie os TRÊS formulários com os dados do POST
            fornecedor_data = {
                'subcategoria': subcategoria_model,
            }
            fornecedor_form = FornecedorPrestadorForm(fornecedor_data)
            fornecedor_servico_form = FornecedorServicoForm(request.POST) # Novo formulário
            trabalhador_form = TrabalhadorForm(request.POST, request.FILES)
            
            # 3. Valide os TRÊS formulários
            if fornecedor_form.is_valid() and fornecedor_servico_form.is_valid() and trabalhador_form.is_valid():
                try:
                    # Usar transaction.atomic para garantir que tudo seja salvo ou nada
                    with transaction.atomic():
                        # a. Salva o Fornecedor principal primeiro para obter um ID
                        fornecedor_instance = fornecedor_form.save()
                        
                        # b. Salva o FornecedorServico, vinculando-o ao Fornecedor criado
                        servico_instance = fornecedor_servico_form.save(commit=False)
                        servico_instance.fornecedor = fornecedor_instance
                        servico_instance.save()
                        
                        # c. Salva o Trabalhador específico, também vinculando-o
                        trabalhador_instance = trabalhador_form.save(commit=False)
                        trabalhador_instance.fornecedor = fornecedor_instance
                        trabalhador_instance.save()
                    
                    # Se tudo deu certo, redireciona
                    return redirect("fornecedores_cadastrados")
                
                except Exception as e:
                    # Se ocorrer um erro durante o salvamento
                    fornecedor_form.add_error(None, f"Ocorreu um erro inesperado ao salvar: {e}")
            else:
                # Se a validação falhar, imprima os erros para depuração
                print("--- ERROS DE VALIDAÇÃO ---")
                print(f"Fornecedor Form: {fornecedor_form.errors}")
                print(f"Serviço Form: {fornecedor_servico_form.errors}")
                if trabalhador_form:
                    print(f"Trabalhador Form: {trabalhador_form.errors}")
                print("--------------------------")

            # Se a validação falhar, a view continua e renderiza os formulários com os erros
            # Atribuir o formulário do trabalhador com erro à variável de contexto correta
            if subcategoria_slug == "trabalhador_clt": clt_form = trabalhador_form
            elif subcategoria_slug == "pessoa_juridica": pj_form = trabalhador_form
            elif subcategoria_slug == "mei": mei_form = trabalhador_form
            elif subcategoria_slug == "autonomo": autonomo_form = trabalhador_form
            elif subcategoria_slug == "associado": associado_form = trabalhador_form
            

    # Lógica para GET (ou se o POST falhar)
    fornecedores_list = Fornecedor.objects.select_related('visitante', 'fornecedor_servico').prefetch_related(
        'trabalhadores_clt', 'pessoas_juridicas', 'meis', 'autonomos', 'associados'
    ).all().order_by('-id') # Adicionar um order_by é bom para paginação

    # Aplicar paginação
    paginator = Paginator(fornecedores_list, 25) # 25 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        "page_obj": page_obj, # Enviar page_obj
        "fornecedores": page_obj, # Manter 'fornecedores' para compatibilidade
        "fornecedor_prestador_form": fornecedor_form,
        "fornecedor_servico_form": fornecedor_servico_form, # Passa o form para o contexto
        "clt_form": clt_form,
        "pj_form": pj_form,
        "mei_form": mei_form,
        "autonomo_form": autonomo_form,
        "associado_form": associado_form,
        "filtros": request.session.get('fornecedores_filtros', {}), # Enviar filtros
    }
    return render(request, "patrimonio/fornecedores_cadastrados.html", context)



@login_required
def modal_editar_fornecedor_completo(request, pk):
    """
    View para edição completa de fornecedor com todas as subcategorias
    """
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    
    if request.method == 'POST':
        return processar_edicao_fornecedor(request, fornecedor)
    else:
        return carregar_dados_fornecedor(request, fornecedor)

def processar_edicao_fornecedor(request, fornecedor):
    try:
        with transaction.atomic():
            fornecedor.status = request.POST.get('status')
            fornecedor.save()
            
            validade_meses = request.POST.get('validade_meses')
            data_validade_str = request.POST.get('data_validade')

            if validade_meses or data_validade_str:
                integracao, created = Integracao.objects.get_or_create(fornecedor=fornecedor)
                
                if validade_meses:
                    integracao.validade_meses = int(validade_meses)
                
                # Se o usuário editar manualmente a data de validade
                if data_validade_str:
                    try:
                        integracao.data_validade = datetime.strptime(data_validade_str, "%Y-%m-%d").date()
                    except ValueError:
                        pass  # ignora formato inválido

                # Se ainda não tiver data de integração, define agora
                if not integracao.data_integracao:
                    integracao.data_integracao = timezone.now().date()
                
                integracao.save()

            if fornecedor.categoria == 'VISITANTE':
                return processar_edicao_visitante(request, fornecedor)

            elif fornecedor.categoria == 'FORNECEDOR':
                trabalhador = fornecedor.trabalhador_relacionado
                if trabalhador:
                    trabalhador.nome_representante = request.POST.get('nome_representante', trabalhador.nome_representante)

                    foto_base64 = request.POST.get('foto_representante_base64')
                    if foto_base64 and foto_base64.startswith('data:image'):
                        try:
                            format, imgstr = foto_base64.split(';base64,')
                            ext = format.split('/')[-1]
                            img_data = base64.b64decode(imgstr)
                            filename = f'representante_{fornecedor.id}_{uuid.uuid4().hex[:8]}.{ext}'
                            trabalhador.foto_representante.save(
                                filename,
                                ContentFile(img_data),
                                save=False
                            )
                        except Exception as e:
                            print(f"Erro ao processar foto do representante: {e}")

                    trabalhador.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Fornecedor atualizado com sucesso!'
                })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao processar edição: {str(e)}'
        })


def processar_edicao_visitante(request, fornecedor):
    """
    Processa edição específica para visitante
    """
    try:
        visitante = fornecedor.visitante
        
        # Atualizar dados do visitante
        visitante.nome = request.POST.get('nome', '')
        visitante.documento = request.POST.get('documento', '')
        visitante.motivo_visita = request.POST.get('motivo_visita', '')
        
        # Processar foto da webcam se fornecida
        foto_base64 = request.POST.get('foto_visitante_base64')
        if foto_base64 and foto_base64.startswith('data:image'):
            try:
                # Extrair dados da imagem base64
                format, imgstr = foto_base64.split(';base64,')
                ext = format.split('/')[-1]
                
                # Decodificar e salvar
                img_data = base64.b64decode(imgstr)
                filename = f'visitante_{fornecedor.id}_{uuid.uuid4().hex[:8]}.{ext}'
                
                visitante.foto_visitante.save(
                    filename,
                    ContentFile(img_data),
                    save=False
                )
            except Exception as e:
                print(f"Erro ao processar foto do visitante: {e}")
        
        visitante.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Visitante atualizado com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao atualizar visitante: {str(e)}'
        })

def processar_edicao_fornecedor_servico(request, fornecedor):
    """
    Processa edição específica para fornecedor/prestador de serviços
    """
    try:
        # Atualizar dados da empresa (se existir)
        if hasattr(fornecedor, 'fornecedor_servico'):
            fornecedor_servico = fornecedor.fornecedor_servico
            fornecedor_servico.nome_empresa = request.POST.get('nome_empresa', '')
            fornecedor_servico.atividade_servico = request.POST.get('atividade_servico', '')
            fornecedor_servico.save()
        
        # Processar dados do representante baseado na subcategoria
        trabalhador = fornecedor.trabalhador_relacionado
        
        if trabalhador:
            # Atualizar nome do representante
            trabalhador.nome_representante = request.POST.get('nome_representante', '')
            
            # Processar foto da webcam se fornecida
            foto_base64 = request.POST.get('foto_representante_base64')
            if foto_base64 and foto_base64.startswith('data:image'):
                try:
                    # Extrair dados da imagem base64
                    format, imgstr = foto_base64.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    # Decodificar e salvar
                    img_data = base64.b64decode(imgstr)
                    filename = f'representante_{fornecedor.id}_{uuid.uuid4().hex[:8]}.{ext}'
                    
                    trabalhador.foto_representante.save(
                        filename,
                        ContentFile(img_data),
                        save=False
                    )
                except Exception as e:
                    print(f"Erro ao processar foto do representante: {e}")
            
            # Processar campos específicos por subcategoria
            if fornecedor.subcategoria == 'CLT':
                trabalhador.descricao_cargo = request.POST.get('descricao_cargo', '')
                
                # Processar arquivos se fornecidos
                if 'documento_identificacao' in request.FILES:
                    trabalhador.documento_identificacao = request.FILES['documento_identificacao']
                if 'aso' in request.FILES:
                    trabalhador.aso = request.FILES['aso']
                    
            elif fornecedor.subcategoria == 'PJ':
                # Processar arquivos específicos de PJ
                if 'documento_identificacao' in request.FILES:
                    trabalhador.documento_identificacao = request.FILES['documento_identificacao']
                if 'cnpj' in request.FILES:
                    trabalhador.cnpj = request.FILES['cnpj']
                    
            elif fornecedor.subcategoria == 'MEI':
                # Processar arquivos específicos de MEI
                if 'documento_identificacao' in request.FILES:
                    trabalhador.documento_identificacao = request.FILES['documento_identificacao']
                if 'certificado_mei' in request.FILES:
                    trabalhador.certificado_mei = request.FILES['certificado_mei']
                    
            elif fornecedor.subcategoria == 'AUTONOMO':
                # Processar arquivos específicos de Autônomo
                if 'documento_identificacao' in request.FILES:
                    trabalhador.documento_identificacao = request.FILES['documento_identificacao']
                if 'declaracao_autonomo' in request.FILES:
                    trabalhador.declaracao_autonomo = request.FILES['declaracao_autonomo']
                    
            elif fornecedor.subcategoria == 'ASSOCIADO':
                # Processar arquivos específicos de Associado
                if 'documento_identificacao' in request.FILES:
                    trabalhador.documento_identificacao = request.FILES['documento_identificacao']
                if 'contrato_associacao' in request.FILES:
                    trabalhador.contrato_associacao = request.FILES['contrato_associacao']
            
            trabalhador.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Fornecedor atualizado com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao atualizar fornecedor: {str(e)}'
        })

@login_required
def carregar_dados_fornecedor(request, pk):
    """
    Carrega os dados do fornecedor para exibição no modal, 
    renderizando o HTML do formulário e retornando-o no JSON.
    """
    try:
        fornecedor = get_object_or_404(Fornecedor, pk=pk)
        # Busca a última integração (se existir)
        ultima_integracao = fornecedor.integracoes.order_by('-data_integracao').first()

        dados = {
            'id': fornecedor.id,
            'categoria': fornecedor.categoria,
            'subcategoria': fornecedor.subcategoria,
            'status': fornecedor.status,
            'validade_meses': ultima_integracao.validade_meses if ultima_integracao else None,
        }
        
        # Carregar dados específicos por categoria
        if fornecedor.categoria == 'VISITANTE' and hasattr(fornecedor, 'visitante'):
            visitante = fornecedor.visitante
            dados['visitante'] = {
                'nome': visitante.nome,
                'documento': visitante.documento,
                'motivo_visita': visitante.motivo_visita,
                'foto_visitante': visitante.foto_visitante.url if visitante.foto_visitante else None,
            }
            
        elif fornecedor.categoria == 'FORNECEDOR':
            # Dados da empresa
            if hasattr(fornecedor, 'fornecedor_servico'):
                fornecedor_servico = fornecedor.fornecedor_servico
                dados['fornecedor_servico'] = {
                    'nome_empresa': fornecedor_servico.nome_empresa,
                    'atividade_servico': fornecedor_servico.atividade_servico,
                }
            
            # Dados do trabalhador relacionado
            trabalhador = fornecedor.trabalhador_relacionado
            if trabalhador:
                dados['trabalhador_relacionado'] = {
                    'nome_representante': trabalhador.nome_representante,
                    'foto_representante': trabalhador.foto_representante.url if trabalhador.foto_representante else None,
                }
                
                # Adicionar campos específicos por subcategoria
                if fornecedor.subcategoria == 'CLT':
                    dados['trabalhador_relacionado']['descricao_cargo'] = getattr(trabalhador, 'descricao_cargo', '')
                    dados['trabalhador_relacionado']['documento_identificacao'] = trabalhador.documento_identificacao.url if trabalhador.documento_identificacao else None
                    dados['trabalhador_relacionado']['aso'] = trabalhador.aso.url if hasattr(trabalhador, 'aso') and trabalhador.aso else None
                        
                elif fornecedor.subcategoria == 'PJ':
                    dados['trabalhador_relacionado']['documento_identificacao'] = trabalhador.documento_identificacao.url if trabalhador.documento_identificacao else None
                    dados['trabalhador_relacionado']['cnpj'] = trabalhador.cnpj.url if hasattr(trabalhador, 'cnpj') and trabalhador.cnpj else None
                        
                elif fornecedor.subcategoria == 'MEI':
                    dados['trabalhador_relacionado']['documento_identificacao'] = trabalhador.documento_identificacao.url if trabalhador.documento_identificacao else None
                    dados['trabalhador_relacionado']['certificado_mei'] = trabalhador.certificado_mei.url if hasattr(trabalhador, 'certificado_mei') and trabalhador.certificado_mei else None
                        
                elif fornecedor.subcategoria == 'AUTONOMO':
                    dados['trabalhador_relacionado']['documento_identificacao'] = trabalhador.documento_identificacao.url if trabalhador.documento_identificacao else None
                    dados['trabalhador_relacionado']['declaracao_autonomo'] = trabalhador.declaracao_autonomo.url if hasattr(trabalhador, 'declaracao_autonomo') and trabalhador.declaracao_autonomo else None
                        
                elif fornecedor.subcategoria == 'ASSOCIADO':
                    dados['trabalhador_relacionado']['documento_identificacao'] = trabalhador.documento_identificacao.url if trabalhador.documento_identificacao else None
                    dados['trabalhador_relacionado']['contrato_associacao'] = trabalhador.contrato_associacao.url if hasattr(trabalhador, 'contrato_associacao') and trabalhador.contrato_associacao else None

        # Renderizar o HTML do formulário
        form_html = render_to_string(
            'patrimonio/includes/modal_edicao_fornecedor_form_content.html', 
            {'fornecedor': fornecedor}, 
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'dados': dados,
            'form_html': form_html
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao carregar dados: {str(e)}'
        })

# Função auxiliar para processar imagens base64
def processar_imagem_base64(base64_string, prefix="foto"):
    """
    Converte string base64 em arquivo de imagem
    """
    if not base64_string or not base64_string.startswith('data:image'):
        return None
    
    try:
        # Extrair formato e dados
        format, imgstr = base64_string.split(';base64,')
        ext = format.split('/')[-1]
        
        # Decodificar
        img_data = base64.b64decode(imgstr)
        
        # Gerar nome único
        filename = f'{prefix}_{uuid.uuid4().hex[:8]}.{ext}'
        
        return ContentFile(img_data, name=filename)
        
    except Exception as e:
        print(f"Erro ao processar imagem base64: {e}")
        return None

@login_required
def detalhes_entrada(request, entrada_id):
    entrada = get_object_or_404(EntradaFornecedor, pk=entrada_id)
    return render(request, 'patrimonio/detalhes_entrada.html', {'entrada': entrada})

@login_required
def excluir_entrada(request, pk):
    entrada = get_object_or_404(EntradaFornecedor, pk=pk)
    if request.method == "POST":
        entrada.delete()
        return redirect('controle_visitantes')  # redirecione para onde achar adequado
    return render(request, '/confirmar_exclusao.html', {'entrada': entrada})

