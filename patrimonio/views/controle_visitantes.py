from django.contrib.auth.decorators import login_required
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from patrimonio.forms import FornecedorForm, VisitanteForm, EntregaForm, EntradaFornecedorForm, FornecedorPrestadorForm, TrabalhadorCLTForm, PessoaJuridicaForm, MEIForm, AutonomoForm, AssociadoForm, FornecedorServicoForm
from patrimonio.models import Fornecedor, EntradaFornecedor, Visitante, Entrega, TrabalhadorCLT, PessoaJuridica, MEI, Autonomo, Associado
from patrimonio.utils import process_webcam_photo, enviar_alerta_vencimentos
from django.core.files.base import ContentFile
import base64
import uuid

@login_required
def controle_visitantes(request):
    hoje = timezone.now().date()

    # Atualiza status automaticamente
    Fornecedor.objects.filter(data_validade__lte=hoje, status='Integrado').update(status='Pendente')

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

    fornecedores = Fornecedor.objects.select_related(
        'visitante',           # Carrega o relacionamento com Visitante
        'fornecedor_servico'   # Carrega o relacionamento com FornecedorServico
    ).all()

    entradas = EntradaFornecedor.objects.all().order_by('-data', '-horario_entrada')

    context = {
        'form_fornecedor': form_fornecedor,
        'form_visitante': form_visitante,
        'form_entrega': form_entrega,
        'form_entrada': form_entrada, # O form_entrada agora contém a lista ordenada
        'fornecedores': fornecedores,
        'entradas': entradas,
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
def fornecedores_cadastrados(request):
    # 1. Inicialize todos os formulários que a página pode precisar
    fornecedor_form = FornecedorPrestadorForm()
    clt_form = TrabalhadorCLTForm()
    pj_form = PessoaJuridicaForm()
    mei_form = MEIForm()
    autonomo_form = AutonomoForm()
    associado_form = AssociadoForm()
    # Adicione o form de serviço também, caso precise dele no futuro
    fornecedor_servico_form = FornecedorServicoForm()

    if request.method == "POST":
        print("POST recebido:", request.POST)  # Debug
        print("FILES recebidos:", request.FILES)  # Debug
        
        # Extrair dados básicos do POST
        categoria = request.POST.get("categoria")
        subcategoria_slug = request.POST.get("subcategoria")
        validade_meses = request.POST.get("validade_meses")
        
        print(f"Categoria: {categoria}")  # Debug
        print(f"Subcategoria recebida: {subcategoria_slug}")  # Debug
        print(f"Validade meses: {validade_meses}")  # Debug

        # CORREÇÃO: Mapeamento correto dos valores do HTML para os formulários
        form_map = {
            "trabalhador_clt": TrabalhadorCLTForm,
            "pessoa_juridica": PessoaJuridicaForm,
            "mei": MEIForm,
            "autonomo": AutonomoForm,
            "associado": AssociadoForm,
            "fornecedor_servico": FornecedorServicoForm,
        }

        # CORREÇÃO: Mapeamento dos valores do HTML para os valores do modelo
        subcategoria_model_map = {
            "trabalhador_clt": "CLT",
            "pessoa_juridica": "PJ",
            "mei": "MEI",
            "autonomo": "AUTONOMO",
            "associado": "ASSOCIADO",
            "fornecedor_servico": "FORNECEDOR_SERVICO",
        }

        trabalhador_form = None # Inicializa como None

        if categoria == "FORNECEDOR" and subcategoria_slug in form_map:
            # Criar o fornecedor primeiro
            fornecedor_data = {
                'categoria': categoria,
                'subcategoria': subcategoria_model_map.get(subcategoria_slug),
                'validade_meses': validade_meses
            }
            
            print(f"Dados do fornecedor: {fornecedor_data}")  # Debug
            
            # Criar formulário do fornecedor com dados corretos
            fornecedor_form = FornecedorPrestadorForm(fornecedor_data)
            
            TrabalhadorForm = form_map[subcategoria_slug]
            # 3. Preencha o formulário do trabalhador específico com os dados do POST
            trabalhador_form = TrabalhadorForm(request.POST, request.FILES)
            
            print(f"Formulário criado: {TrabalhadorForm.__name__}")  # Debug
            print(f"Dados do fornecedor válidos: {fornecedor_form.is_valid()}")  # Debug
            print(f"Dados do trabalhador válidos: {trabalhador_form.is_valid()}")  # Debug
            
            if not fornecedor_form.is_valid():
                print(f"Erros do fornecedor: {fornecedor_form.errors}")  # Debug
            if not trabalhador_form.is_valid():
                print(f"Erros do trabalhador: {trabalhador_form.errors}")  # Debug

            # 4. Valide AMBOS os formulários
            if fornecedor_form.is_valid() and trabalhador_form.is_valid():
                try:
                    with transaction.atomic():
                        # Salvar o fornecedor primeiro
                        fornecedor_instance = fornecedor_form.save()
                        
                        # Salvar o trabalhador vinculado ao fornecedor
                        trabalhador_instance = trabalhador_form.save(commit=False)
                        trabalhador_instance.fornecedor = fornecedor_instance
                        trabalhador_instance.save()
                        
                        print("Salvamento realizado com sucesso!")  # Debug
                    
                    return redirect("fornecedores_cadastrados") # SUCESSO!
                except Exception as e:
                    print(f"Erro na transação: {e}") # Log para depuração
                    # Adicione um erro não-campo ao formulário para notificar o usuário
                    fornecedor_form.add_error(None, f"Ocorreu um erro inesperado ao salvar: {e}")
            else:
                print("Formulários inválidos:")  # Debug
                print(f"Fornecedor form errors: {fornecedor_form.errors}")
                if trabalhador_form:
                    print(f"Trabalhador form errors: {trabalhador_form.errors}")

            # 5. SE A VALIDAÇÃO FALHAR, a view continua aqui.
            # A mágica é que as variáveis `fornecedor_form` e `trabalhador_form`
            # agora contêm os dados preenchidos e os dicionários de erros.
            # Precisamos garantir que o formulário correto seja passado para o contexto.
            
            if subcategoria_slug == "trabalhador_clt": clt_form = trabalhador_form
            elif subcategoria_slug == "pessoa_juridica": pj_form = trabalhador_form
            elif subcategoria_slug == "mei": mei_form = trabalhador_form
            elif subcategoria_slug == "autonomo": autonomo_form = trabalhador_form
            elif subcategoria_slug == "associado": associado_form = trabalhador_form
            elif subcategoria_slug == "fornecedor_servico": fornecedor_servico_form = trabalhador_form

    # Lógica para GET (ou se o POST falhar)
    fornecedores = Fornecedor.objects.select_related('visitante', 'fornecedor_servico').all().order_by('-data_integracao')

    context = {
        "fornecedores": fornecedores,
        "fornecedor_prestador_form": fornecedor_form, # Passa o formulário (vazio ou com erros)
        "clt_form": clt_form,
        "pj_form": pj_form,
        "mei_form": mei_form,
        "autonomo_form": autonomo_form,
        "associado_form": associado_form,
        "fornecedor_servico_form": fornecedor_servico_form,
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
    """
    Processa a edição do fornecedor via POST
    """
    try:
        with transaction.atomic():
            # Atualizar dados básicos do fornecedor
            fornecedor.validade_meses = request.POST.get('validade_meses')
            fornecedor.status = request.POST.get('status')
            fornecedor.save()
            
            if fornecedor.categoria == 'VISITANTE':
                return processar_edicao_visitante(request, fornecedor)
            elif fornecedor.categoria == 'FORNECEDOR':
                return processar_edicao_fornecedor_servico(request, fornecedor)
                
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

        dados = {
            'id': fornecedor.id,
            'categoria': fornecedor.categoria,
            'subcategoria': fornecedor.subcategoria,
            'validade_meses': fornecedor.validade_meses,
            'status': fornecedor.status,
            'data_integracao': fornecedor.data_integracao.strftime('%Y-%m-%d') if fornecedor.data_integracao else '',
            'data_validade': fornecedor.data_validade.strftime('%Y-%m-%d') if fornecedor.data_validade else '',
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

