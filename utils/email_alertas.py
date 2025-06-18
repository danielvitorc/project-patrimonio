from django.core.mail import send_mail
from django.utils import timezone
from patrimonio.models import Fornecedor
from django.conf import settings
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


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

        # Busca usuários com e-mail válido
        destinatarios = list(
            User.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True)
        )

        if not destinatarios:
            print("⚠️ Nenhum destinatário válido encontrado.")
            return

        send_mail(
            subject='[Alerta] Fornecedores com validade vencida ou próxima',
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False,
        )
        print(f"✅ Alerta enviado para: {', '.join(destinatarios)}")
