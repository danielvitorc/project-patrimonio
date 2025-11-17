from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from patrimonio.forms import QuestionarioIntegracaoForm, CORRECT_ANSWERS
from patrimonio.models import Fornecedor, Integracao, IntegracaoToken, FornecedorServico, QuestionarioIntegracao
from patrimonio.decorators import verifica_token_valido
from datetime import timedelta, datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from fpdf import FPDF
from PIL import Image
import io, os
import tempfile


@login_required
def gerar_link_integracao(request, fornecedor_id):
    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)

    if fornecedor.status not in ["Sem integração", "Pendente"]:
        return JsonResponse({"erro": "Este fornecedor já está integrado."}, status=400)

    # Pega valor enviado pelo usuário
    validade_meses_input = request.POST.get("validade_meses")
    validade_meses = int(validade_meses_input) if validade_meses_input else 12

    # Cria ou busca integração usando o valor informado
    integracao, created = Integracao.objects.get_or_create(
        fornecedor=fornecedor,
        defaults={"validade_meses": validade_meses}
    )

    # Atualiza validade se integração já existia e usuário passou novo valor
    if not created and validade_meses_input:
        integracao.validade_meses = validade_meses
        integracao.save(update_fields=["validade_meses"])

    # Verifica se já existe token válido
    token_existente = integracao.tokens.filter(expira_em__gt=timezone.now()).first()
    if token_existente:
        link = request.build_absolute_uri(reverse("token_login", args=[integracao.uuid_link]))
        return JsonResponse({
            "link": link,
            "token": token_existente.token,
            "mensagem": "Um link já foi gerado nas últimas 24 horas."
        })

    # Cria novo token válido por 24h
    token = IntegracaoToken.objects.create(
        integracao=integracao,
        criado_por=request.user,
        expira_em=timezone.now() + timedelta(hours=24)
    )

    link = request.build_absolute_uri(reverse("token_login", args=[integracao.uuid_link]))

    return JsonResponse({
        "link": link,
        "token": token.token,
        "mensagem": "Novo link de integração gerado com sucesso.",
        "validade_usada": validade_meses,
    })


def token_login(request, uuid_link):
    integracao = get_object_or_404(Integracao, uuid_link=uuid_link)
    
    token_input = request.GET.get("token") if request.method == "GET" else request.POST.get("token")
    
    if not token_input:
        return render(request, "patrimonio/integracao/token_login.html", {"uuid_link": uuid_link})
    
    token_obj = IntegracaoToken.objects.filter(integracao=integracao, token=token_input).first()
    
    if not token_obj or not token_obj.is_valid():
        return redirect(f"{reverse('token_login', args=[uuid_link])}?token={token_input}")

    # Redireciona para orientações após autenticar
    return redirect(f"{reverse('integracao_orientacoes', args=[uuid_link])}?token={token_input}")


@verifica_token_valido
def integracao_orientacoes(request, uuid_link):
    integracao = request.integracao
    token_input = request.integracao_token_value

    return render(request, "patrimonio/integracao/integracao_orientacoes.html", {
        "integracao": integracao,
        "token": token_input
    })


@verifica_token_valido
def integracao_video(request, uuid_link):
    integracao = request.integracao
    token_input = request.integracao_token_value

    return render(request, "patrimonio/integracao/integracao_video.html", {
        "integracao": integracao,
        "token": token_input
    })


@verifica_token_valido
def pagina_integracao_externa(request, uuid_link):
    integracao = request.integracao
    token_input = request.integracao_token_value
    mensagem = None

    # Formulário
    if request.method == "POST":
        form = QuestionarioIntegracaoForm(request.POST)
        if form.is_valid():
            q1_ok = form.cleaned_data['questao1'] == CORRECT_ANSWERS['questao1']
            q2_ok = form.cleaned_data['questao2'] == CORRECT_ANSWERS['questao2']
            q3_ok = form.cleaned_data['questao3'] == CORRECT_ANSWERS['questao3']

            questionario, criado = QuestionarioIntegracao.objects.get_or_create(
                integracao=integracao,
                defaults={
                    'questao1': q1_ok,
                    'questao2': q2_ok,
                    'questao3': q3_ok,
                }
            )

            # Se quiser atualizar os valores caso já exista
            if not criado:
                questionario.questao1 = q1_ok
                questionario.questao2 = q2_ok
                questionario.questao3 = q3_ok
                questionario.save(update_fields=['questao1', 'questao2', 'questao3'])
                
            questionario.save()

            # Invalida token após uso
            token_obj = IntegracaoToken.objects.get(integracao=integracao, token=token_input)
            token_obj.expira_em = timezone.now()
            token_obj.save(update_fields=["expira_em"])

            return redirect('integracao_sucesso', integracao_id=integracao.id)
    else:
        form = QuestionarioIntegracaoForm()

    fornecedor = integracao.fornecedor

    try:
        fornecedorservico = fornecedor.fornecedor_servico
    except FornecedorServico.DoesNotExist:
        fornecedorservico = None

    return render(request, "patrimonio/integracao/integracao_externa.html", {
        "fornecedor": fornecedor,
        "fornecedorservico": fornecedorservico,
        "integracao": integracao,
        "form": form,
        "token": token_input,
        "mensagem": mensagem
    })


def integracao_sucesso(request, integracao_id):
    integracao = get_object_or_404(Integracao, id=integracao_id)
    return render(request, "patrimonio/integracao/integracao_sucesso.html", {"integracao": integracao})
    

def gerar_certificado_integracao(request, integracao_id):
    integracao = get_object_or_404(Integracao, id=integracao_id)

    class PDF(FPDF):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Caminhos diretos
            self.caminho_fundo = 'patrimonio/static/patrimonio/img/1background.png'

        def header(self):
            if os.path.exists(self.caminho_fundo):
                # --- aplica opacidade ---
                fundo = Image.open(self.caminho_fundo).convert("RGBA")
                alpha = fundo.getchannel("A")
                alpha = alpha.point(lambda p: int(p * 0.25))  # 25% opacidade
                fundo.putalpha(alpha)

                # salva imagem temporária
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
                    fundo.save(temp.name, format="PNG")
                    temp_path = temp.name

                # insere imagem opaca no PDF
                self.image(temp_path, x=60, y=30, w=180, h=150)
                os.remove(temp_path)

            # Moldura
            self.set_line_width(1)
            self.set_draw_color(34, 49, 63)
            self.rect(5.0, 5.0, 287.0, 200.0)
            self.rect(8.0, 8.0, 281.0, 194.0)

    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # --- FUNDO AZUL ATRÁS DA LOGO ---
    pdf.set_fill_color(52, 152, 219)  # azul suave (RGB)


    # --- TÍTULO ---
    pdf.set_y(40)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, 'CERTIFICADO DE INTEGRAÇÃO', 0, 1, 'C')

    pdf.ln(5)
    pdf.set_font('Arial', '', 16)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 10, 'Confirmação de Treinamento via Vídeo', 0, 1, 'C')
    pdf.ln(15)

    # --- CORPO ---
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(52, 73, 94)
    pdf.multi_cell(0, 8, "Certificamos, para os devidos fins, que", 0, 'C')
    pdf.ln(5)

    representante = integracao.fornecedor.trabalhador_relacionado
    nome_participante = representante.nome_representante.upper() if representante else "PARTICIPANTE DESCONHECIDO"
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, nome_participante, 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(52, 73, 94)
    texto_final = (
        "concluiu com êxito o treinamento de integração de segurança "
        "por meio do vídeo institucional da empresa Norte Tech - "
        "Serviços em Energia Ltda., estando apto(a) a ingressar nas áreas operacionais."
    )
    pdf.multi_cell(0, 8, texto_final, 0, 'C')
    pdf.ln(20)

    # --- DATA ---
    meses = {
        "January": "Janeiro", "February": "Fevereiro", "March": "Março",
        "April": "Abril", "May": "Maio", "June": "Junho",
        "July": "Julho", "August": "Agosto", "September": "Setembro",
        "October": "Outubro", "November": "Novembro", "December": "Dezembro"
    }
    if integracao.data_integracao:
        nome_mes_en = integracao.data_integracao.strftime("%B")
        nome_mes_pt = meses.get(nome_mes_en, nome_mes_en)
        data_formatada = integracao.data_integracao.strftime(f"%d de {nome_mes_pt} de %Y")
    else:
        data_formatada = "Data não registrada"

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Manaus, {data_formatada}", 0, 1, 'C')

    # --- RODAPÉ ---
    pdf.ln(15)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(149, 165, 166)
    pdf.cell(0, 10, 'Norte Tech - Serviços em Energia LTDA.', 0, 1, 'C')

    # --- RETORNA PDF ---
    pdf_bytes = pdf.output(dest='S').encode('latin1')

    nome_arquivo = (representante.nome_representante if representante else "participante").replace(" ", "_")
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="certificado_{nome_arquivo}.pdf"'
    return response



