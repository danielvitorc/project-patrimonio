# project-patrimonio/patrimonio/views/chave.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from patrimonio.forms import ControleChavesForm, DevolucaoChaveForm
from patrimonio.models import ControleChaves, Colaborador
from django.core.paginator import Paginator  # 1. Importar Paginator

@login_required
def entrega_de_chave(request):
    # 1. Busca inicial de dados
    # Mudar para 'chaves_list' para não conflitar
    chaves_list = ControleChaves.objects.all().order_by('-id')
    form_chave = ControleChavesForm()

    # 2. Processar entrega (POST)
    if request.method == 'POST' and 'form_tipo' in request.POST and request.POST['form_tipo'] == 'entrega':
        form_chave = ControleChavesForm(request.POST, request.FILES)
        if form_chave.is_valid():
            controle = form_chave.save(commit=False)
            controle.situacao = "RETIRADO"
            controle.save()
            messages.success(request, "Entrega registrada com sucesso!")
            return redirect('entrega_de_chave')
        else:
            # Se o form de entrega falhar, recarregamos tudo com paginação
            messages.error(request, "Erro ao registrar entrega.")
            # Aplicar paginação
            paginator = Paginator(chaves_list, 25) # 25 por página
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            # Anexar forms de devolução apenas para a página atual
            for chave in page_obj:
                if chave.situacao == "RETIRADO":
                    chave.form_devolucao = DevolucaoChaveForm(instance=chave)
                else:
                    chave.form_devolucao = None
            
            return render(request, 'patrimonio/entrega_de_chave.html', {
                'form_chave': form_chave, # O form com erro
                'page_obj': page_obj,      # O objeto de paginação
            })

    # 3. Processar devolução (POST)
    elif request.method == 'POST' and 'form_tipo' in request.POST and request.POST['form_tipo'] == 'devolucao':
        chave_id = request.POST.get('chave_id')
        chave_para_devolver = get_object_or_404(ControleChaves, id=chave_id)
        form_devolucao = DevolucaoChaveForm(request.POST, request.FILES, instance=chave_para_devolver)
        
        if form_devolucao.is_valid():
            devolucao = form_devolucao.save(commit=False)
            devolucao.data_devolucao = timezone.now()
            devolucao.situacao = "DEVOLVIDO"
            devolucao.save()
            messages.success(request, "Chave devolvida com sucesso!")
            return redirect('entrega_de_chave')
        else:
            # Se o form de devolução falhar, recarregamos com paginação
            messages.error(request, "Erro ao registrar devolução. Verifique os campos.")
            
            # Aplicar paginação
            paginator = Paginator(chaves_list, 25) # 25 por página
            # Tenta pegar a página do GET, mesmo sendo um POST, caso a URL tenha
            page_number = request.GET.get('page') 
            page_obj = paginator.get_page(page_number)

            for c in page_obj: # Iterar sobre a página atual
                if c.id == chave_para_devolver.id:
                    c.form_devolucao = form_devolucao # Anexa o form com erro
                elif c.situacao == "RETIRADO":
                    c.form_devolucao = DevolucaoChaveForm(instance=c)
                else:
                    c.form_devolucao = None
            
            return render(request, 'patrimonio/entrega_de_chave.html', {
                'form_chave': form_chave, # Form de entrega (novo)
                'page_obj': page_obj,      # O objeto de paginação
            })

    # 4. Lógica para GET (nenhum POST)
    
    # Aplicar paginação
    paginator = Paginator(chaves_list, 25) # 25 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Anexa o form de devolução a cada objeto 'chave' APENAS da página atual
    for chave in page_obj:
        if not hasattr(chave, 'form_devolucao'): # Evita sobrescrever form com erro
            if chave.situacao == "RETIRADO":
                chave.form_devolucao = DevolucaoChaveForm(instance=chave)
            else:
                chave.form_devolucao = None

    # Renderiza a página
    return render(request, 'patrimonio/entrega_de_chave.html', {
        'form_chave': form_chave,
        'page_obj': page_obj, # 3. Enviar page_obj ao invés de 'chaves'
    })

@login_required
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
@login_required
def excluir_chave(request, id):
    chave = get_object_or_404(ControleChaves, id=id)
    try:
        chave.delete()
        messages.success(request, "Movimentação de Chave excluído com sucesso.")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao tentar excluir movimentação de chave: {e}")
    return redirect('entrega_de_chave')