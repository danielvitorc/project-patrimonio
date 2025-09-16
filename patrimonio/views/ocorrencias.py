from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from patrimonio.forms import OcorrenciaForm
from patrimonio.models import Ocorrencia

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

