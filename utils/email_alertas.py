from django.core.mail import send_mail
from django.utils import timezone
from patrimonio.models import Fornecedor
from django.conf import settings
from datetime import timedelta

def enviar_alerta_vencimentos():
    hoje = timezone.now().date()
    proximos = Fornecedor.objects.filter(data_validade__lte=hoje + timedelta(days=5))

    if proximos.exists():
        mensagem = "Os seguintes cadastros estão vencidos ou próximos do vencimento:\n\n"
        for f in proximos:
            mensagem += (
                f"- ID {f.id} | Categoria: {f.get_categoria_display()} | "
                f"Validade: {f.data_validade.strftime('%d/%m/%Y')} | Status: {f.status}\n"
            )

        send_mail(
            subject='[Alerta] Fornecedores com validade vencida ou próxima',
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['sistema.agendamento.nortetech@email.com'],  # Troque aqui
            fail_silently=False,
        )
