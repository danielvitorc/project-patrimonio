from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from patrimonio.models import Fornecedor
import pandas as pd

@login_required
def exportar_fornecedores_excel(request, categoria=None):
    """
    View para exportar fornecedores para Excel, com filtro opcional por categoria.
    """
    fornecedores = Fornecedor.objects.select_related(
        'visitante', 'fornecedor_servico', 'entrega'
    ).all().order_by('-data_integracao')

    if categoria:
        fornecedores = fornecedores.filter(categoria=categoria.upper())

    dados_exportacao = []

    for fornecedor in fornecedores:
        linha = {
            'ID': fornecedor.id,
            'Categoria': fornecedor.get_categoria_display(),
            'Data de Integração': fornecedor.data_integracao.strftime('%d/%m/%Y'),
            'Data de Validade': fornecedor.data_validade.strftime('%d/%m/%Y'),
            'Validade (Meses)': fornecedor.validade_meses,
            'Status': fornecedor.status,
        }

        if fornecedor.categoria == 'VISITANTE' and hasattr(fornecedor, 'visitante'):
            visitante = fornecedor.visitante
            linha.update({
                'Nome/Empresa': visitante.nome,
                'Documento': visitante.documento,
                'Motivo da Visita': visitante.motivo_visita,
                'Representante': '',
                'Atividade/Serviço': '',
            })
        elif fornecedor.categoria == 'FORNECEDOR' and hasattr(fornecedor, 'fornecedor_servico'):
            servico = fornecedor.fornecedor_servico
            linha.update({
                'Nome/Empresa': servico.nome_empresa,
                'Documento': servico.documento,
                'Motivo da Visita': '',
                'Representante': servico.nome_representante,
                'Atividade/Serviço': servico.atividade_servico,
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
            'fg_color': '#D7E4BC',
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        worksheet.set_column('A:A', 8)   # ID
        worksheet.set_column('B:B', 15)  # Categoria
        worksheet.set_column('C:C', 30)  # Nome/Empresa
        worksheet.set_column('D:D', 15)  # Data Integração
        worksheet.set_column('E:E', 15)  # Data Validade
        worksheet.set_column('F:F', 12)  # Validade Meses
        worksheet.set_column('G:G', 12)  # Status
        worksheet.set_column('H:H', 20)  # Documento
        worksheet.set_column('I:I', 25)  # Motivo da Visita
        worksheet.set_column('J:J', 25)  # Representante
        worksheet.set_column('K:K', 25)  # Atividade/Serviço

    return response

@login_required
def exportar_fornecedores_servico_excel(request):
    return exportar_fornecedores_excel(request, categoria='FORNECEDOR')
@login_required
def exportar_visitantes_excel(request):
    return exportar_fornecedores_excel(request, categoria='VISITANTE')