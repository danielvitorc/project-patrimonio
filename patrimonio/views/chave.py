from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from patrimonio.forms import ControleChavesForm, DevolucaoChaveForm
from patrimonio.models import ControleChaves, Colaborador

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