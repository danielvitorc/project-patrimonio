# project-patrimonio/patrimonio/views/export_excel.py

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from patrimonio.models import Fornecedor
import pandas as pd

@login_required
def exportar_fornecedores_excel(request, categoria=None):
    """
    View para exportar fornecedores para Excel, com filtro opcional por categoria.
    VERSÃO CORRIGIDA para funcionar com os novos modelos (Integracao, Trabalhador)
    """
    
    # 1. Busca os fornecedores. Removemos o .order_by('-data_integracao') que causava o crash.
    fornecedores_qs = Fornecedor.objects.select_related(
        'visitante', 'fornecedor_servico'
    ).prefetch_related(
        'integracoes', # Carrega as integrações relacionadas
        'trabalhadores_clt', 'pessoas_juridicas', 'meis', 'autonomos', 'associados' # Carrega todos os tipos de trabalhadores
    ).all()

    if categoria:
        fornecedores_qs = fornecedores_qs.filter(categoria=categoria.upper())

    dados_exportacao = []

    # 2. Itera sobre os fornecedores e usa as properties do modelo
    for fornecedor in fornecedores_qs:
        
        # Pega a última integração de forma segura
        ultima_integracao = fornecedor.ultima_integracao
        
        linha = {
            'ID': fornecedor.id,
            'Categoria': fornecedor.get_categoria_display(),
            # CORRIGIDO: Usa as properties do modelo
            'Data de Integração': fornecedor.data_integracao_formatada,
            'Data de Validade': fornecedor.data_validade_formatada,
            'Validade (Meses)': ultima_integracao.validade_meses if ultima_integracao else '',
            'Status': fornecedor.status,
        }

        # Pega o trabalhador (representante) de forma segura
        trabalhador = fornecedor.trabalhador_relacionado

        if fornecedor.categoria == 'VISITANTE' and hasattr(fornecedor, 'visitante'):
            visitante = fornecedor.visitante
            linha.update({
                'Nome/Empresa': visitante.nome,
                'Documento': visitante.documento,
                'Motivo da Visita': visitante.motivo_visita,
                'Representante': '',
                'Atividade/Serviço': '',
            })
        elif fornecedor.categoria == 'FORNECEDOR':
            nome_empresa = ""
            atividade = ""
            nome_rep = ""
            doc_rep = ""
            
            if hasattr(fornecedor, 'fornecedor_servico') and fornecedor.fornecedor_servico:
                nome_empresa = fornecedor.fornecedor_servico.nome_empresa
                atividade = fornecedor.fornecedor_servico.atividade_servico
                
            if trabalhador:
                nome_rep = trabalhador.nome_representante
                # CORRIGIDO: Busca o documento do trabalhador
                if trabalhador.documento_identificacao:
                     doc_rep = "Enviado" # Opcional: trabalhador.documento_identificacao.url
                
            linha.update({
                'Nome/Empresa': nome_empresa,
                'Documento': doc_rep, # CORRIGIDO
                'Motivo da Visita': '',
                'Representante': nome_rep, # CORRIGIDO
                'Atividade/Serviço': atividade, # CORRIGIDO
            })
        else:
            linha.update({
                'Nome/Empresa': '',
                'Documento': '',
                'Motivo da Visita': '',
                'Representante': '',
                'Atividade/Serviço': '',
            })

        dados_exportacao.append(linha)

    df = pd.DataFrame(dados_exportacao)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    filename = 'fornecedores_cadastrados.xlsx'
    if categoria:
        filename = f'{categoria.lower()}_cadastrados.xlsx'

    response['Content-Disposition'] = f'attachment; filename={filename}'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Fornecedores', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Fornecedores']

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC', # Mantém seu estilo original
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Define a largura das colunas (ajustado)
        worksheet.set_column('A:A', 8)   # ID
        worksheet.set_column('B:B', 20)  # Categoria
        worksheet.set_column('C:C', 20)  # Data de Integração
        worksheet.set_column('D:D', 20)  # Data de Validade
        worksheet.set_column('E:E', 12)  # Validade (Meses)
        worksheet.set_column('F:F', 15)  # Status
        worksheet.set_column('G:G', 30)  # Nome/Empresa
        worksheet.set_column('H:H', 15)  # Documento
        worksheet.set_column('I:I', 25)  # Motivo da Visita
        worksheet.set_column('J:J', 30)  # Representante
        worksheet.set_column('K:K', 25)  # Atividade/Serviço

    return response

@login_required
def exportar_fornecedores_servico_excel(request):
    return exportar_fornecedores_excel(request, categoria='FORNECEDOR')
@login_required
def exportar_visitantes_excel(request):
    return exportar_fornecedores_excel(request, categoria='VISITANTE')