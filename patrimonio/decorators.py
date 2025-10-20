from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from patrimonio.models import Integracao, IntegracaoToken
from django.utils import timezone

def verifica_token_valido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # tenta extrair uuid_link dos kwargs ou args (compatível com ambos)
        uuid_link = kwargs.get('uuid_link') or (args[0] if args else None)

        # se a view não usa uuid_link (ex: integracao_sucesso), apenas executa a view
        if not uuid_link:
            return view_func(request, *args, **kwargs)

        integracao = get_object_or_404(Integracao, uuid_link=uuid_link)

        # aceita token em GET ou POST
        token_input = request.GET.get("token") or request.POST.get("token")

        if not token_input:
            # redireciona para tela de login do token (sem anexar token)
            return redirect(f"{reverse('token_login', args=[uuid_link])}")

        token_obj = IntegracaoToken.objects.filter(
            integracao=integracao,
            token=token_input
        ).first()

        if not token_obj or token_obj.expira_em < timezone.now():
            return redirect(f"{reverse('token_login', args=[uuid_link])}")

        # torna objetos disponíveis para a view (evita consultas repetidas)
        request.integracao = integracao
        request.integracao_token = token_obj
        request.integracao_token_value = token_input

        return view_func(request, *args, **kwargs)
    return wrapper
