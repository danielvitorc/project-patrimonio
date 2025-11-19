from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from patrimonio.forms import OcorrenciaForm
from patrimonio.models import Ocorrencia
from django.core.paginator import Paginator

@login_required
def livro_de_ocorrencia(request):

    # 2. BUSCAR A LISTA COMPLETA
    ocorrencias_list = Ocorrencia.objects.all().order_by('-id')
    
    # 3. CRIAR O PAGINATOR (15 itens por página)
    paginator = Paginator(ocorrencias_list, 15)
    
    # 4. PEGAR O NÚMERO DA PÁGINA (da URL, ex: ?page=2)
    page_number = request.GET.get('page')
    
    # 5. OBTER O OBJETO DA PÁGINA
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form_ocorrencia = OcorrenciaForm(request.POST)
        if form_ocorrencia.is_valid():
            ocorrencia = form_ocorrencia.save(commit=False)
            ocorrencia.usuario = request.user
            ocorrencia.save()
            return redirect('livro_de_ocorrencia') # Redireciona para a página 1
    else:
        form_ocorrencia = OcorrenciaForm()

    # 6. ATUALIZAR O CONTEXTO
    return render(request, 'patrimonio/livro_de_ocorrencia.html', {
        'form_ocorrencia': form_ocorrencia, 
        'page_obj': page_obj, # <-- Passa o page_obj em vez de 'ocorrencias'
    })