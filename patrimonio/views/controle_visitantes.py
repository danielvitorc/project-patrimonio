from django.contrib.auth.decorators import login_required
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from patrimonio.forms import FornecedorForm, VisitanteForm, FornecedorServicoForm, EntregaForm, EntradaFornecedorForm
from patrimonio.models import Fornecedor, EntradaFornecedor
from patrimonio.utils import process_webcam_photo, enviar_alerta_vencimentos

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
        # Cria um campo temporário 'nome_ordenado'
        nome_ordenado=Coalesce(
            'visitante__nome', 
            'fornecedor_servico__nome_representante', 
            'entrega__nome_entregador',
            Value('Sem Nome') # Valor padrão para garantir que todos os registros sejam incluídos
        )
    ).order_by('nome_ordenado') # Ordena pelo campo criado

    # 2. Instancie os formulários, passando o queryset para o form_entrada
    form_fornecedor = FornecedorForm()
    form_visitante = VisitanteForm()
    form_fornecedor_servico = FornecedorServicoForm()
    form_entrega = EntregaForm()
    
    # Passe o queryset ordenado para o formulário de entrada
    form_entrada = EntradaFornecedorForm(queryset=fornecedores_ordenados)


    if request.method == 'POST':
        # Novo Fornecedor (esta parte não precisa mudar)
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

    fornecedores = Fornecedor.objects.all()
    entradas = EntradaFornecedor.objects.all().order_by('-data', '-horario_entrada')

    context = {
        'form_fornecedor': form_fornecedor,
        'form_visitante': form_visitante,
        'form_fornecedor_servico': form_fornecedor_servico,
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

@login_required
def fornecedores_cadastrados(request):
    fornecedores = Fornecedor.objects.all().order_by('-data_integracao')
    return render(request, 'patrimonio/fornecedores_cadastrados.html', {'fornecedores': fornecedores})

@login_required
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





