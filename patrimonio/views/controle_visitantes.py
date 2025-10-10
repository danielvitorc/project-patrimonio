from django.contrib.auth.decorators import login_required
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from patrimonio.forms import FornecedorForm, VisitanteForm, EntregaForm, EntradaFornecedorForm, FornecedorPrestadorForm, TrabalhadorCLTForm, PessoaJuridicaForm, MEIForm, AutonomoForm, AssociadoForm, FornecedorServicoForm, QuestionarioIntegracaoForm
from patrimonio.models import Fornecedor, EntradaFornecedor, Visitante, Entrega, TrabalhadorCLT, PessoaJuridica, MEI, Autonomo, Associado, Integracao, IntegracaoToken
from patrimonio.utils import process_webcam_photo, enviar_alerta_vencimentos
from django.core.files.base import ContentFile
from datetime import timedelta
import secrets
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
def gerar_link_integracao(request, fornecedor_id):
    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)

    # ✅ Impede gerar se já estiver integrado
    if fornecedor.status not in ["Sem integração", "Pendente"]:
        return JsonResponse({"erro": "Este fornecedor já está integrado."}, status=400)

    # ✅ Cria ou busca a integração existente, mas SEM definir data_integracao
    integracao, _ = Integracao.objects.get_or_create(
        fornecedor=fornecedor,
        defaults={"validade_meses": 12}  # padrão inicial
    )

    # ✅ Verifica se já existe token válido
    token_existente = integracao.tokens.filter(expira_em__gt=timezone.now()).first()
    if token_existente:
        url = request.build_absolute_uri(
            reverse("pagina_integracao_externa", args=[integracao.uuid_link, token_existente.uuid_link])
        )
        return JsonResponse({
            "link": url,
            "token": token_existente.token,
            "mensagem": "Um link já foi gerado nas últimas 24 horas."
        })

    # ✅ Verifica se já existe validade definida
    validade_meses = integracao.validade_meses or request.POST.get("validade_meses")

    # Se ainda não existir validade (nova integração e o usuário não informou)
    if not validade_meses:
        return JsonResponse({"erro": "Informe a validade (em meses)."}, status=400)

    validade_meses = int(validade_meses)
    integracao.validade_meses = validade_meses
    integracao.save(update_fields=["validade_meses"])

    # ✅ Cria novo token válido por 24h
    token = IntegracaoToken.objects.create(
        integracao=integracao,
        criado_por=request.user,
        expira_em=timezone.now() + timedelta(hours=24)
    )

    url = request.build_absolute_uri(
        reverse("pagina_integracao_externa", args=[integracao.uuid_link, token.uuid_link])
    )

    return JsonResponse({
        "link": url,
        "token": token.token,
        "mensagem": "Novo link de integração gerado com sucesso.",
        "validade_usada": validade_meses,
    })


def pagina_integracao_externa(request, uuid_link, token):
    integracao = get_object_or_404(Integracao, uuid_link=uuid_link)
    token_obj = get_object_or_404(IntegracaoToken, integracao=integracao, uuid_link=token)

    # ✅ Valida o token
    if not token_obj.is_valid():
        return HttpResponse("❌ Token expirado ou inválido. Solicite um novo link de integração.", status=403)

    # ✅ Se o questionário já foi preenchido, bloqueia novo envio
    if hasattr(integracao, "questionario"):
        return HttpResponse("✅ Questionário já foi preenchido para este fornecedor.", status=200)

    if request.method == "POST":
        form = QuestionarioIntegracaoForm(request.POST)
        if form.is_valid():
            questionario = form.save(commit=False)
            questionario.integracao = integracao
            questionario.save()
            return HttpResponse("✅ Questionário enviado com sucesso. Obrigado!", status=200)
    else:
        form = QuestionarioIntegracaoForm()

    return render(request, "patrimonio/integracao_externa.html", {
        "fornecedor": integracao.fornecedor,
        "integracao": integracao,
        "form": form
    })

@login_required
def fornecedores_cadastrados(request):
    # 1. Inicialize todos os formulários que a página pode precisar para o método GET
    fornecedor_form = FornecedorPrestadorForm()
    fornecedor_servico_form = FornecedorServicoForm() # Adicionado aqui para o contexto inicial
    clt_form = TrabalhadorCLTForm()
    pj_form = PessoaJuridicaForm()
    mei_form = MEIForm()
    autonomo_form = AutonomoForm()
    associado_form = AssociadoForm()

    if request.method == "POST":
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
    fornecedores = Fornecedor.objects.select_related('visitante', 'fornecedor_servico').prefetch_related(
        'trabalhadores_clt', 'pessoas_juridicas', 'meis', 'autonomos', 'associados'
    ).all()

    context = {
        "fornecedores": fornecedores,
        "fornecedor_prestador_form": fornecedor_form,
        "fornecedor_servico_form": fornecedor_servico_form, # Passa o form para o contexto
        "clt_form": clt_form,
        "pj_form": pj_form,
        "mei_form": mei_form,
        "autonomo_form": autonomo_form,
        "associado_form": associado_form,
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

