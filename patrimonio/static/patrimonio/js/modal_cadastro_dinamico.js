document.addEventListener('DOMContentLoaded', function() {
    const categoriaSelect = document.getElementById('categoria');
    const subcategoriaSelect = document.getElementById('subcategoria');
    const subcategoriaContainer = document.getElementById('subcategoria-container');
    const formsContainer = document.getElementById('forms-container');

    // ==================================================================
    //           INÍCIO DA CORREÇÃO NOS FORMULÁRIOS DINÂMICOS
    // ==================================================================
    const formularios = {
        'trabalhador_clt': `
            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">1. Dados da Empresa</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="nome_empresa_clt" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_clt" name="nome_empresa" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label for="atividade_servico_clt" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_clt" name="atividade_servico" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card shadow-sm">
                <div class="card-header"><h6 class="mb-0">Dados do Trabalhador CLT</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="nome_representante_clt" class="form-label">Nome do Representante:</label>
                            <input type="text" id="nome_representante_clt" name="nome_representante" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label for="descricao_cargo_clt" class="form-label">Descrição do Cargo:</label>
                            <input type="text" id="descricao_cargo_clt" name="descricao_cargo" class="form-control">
                        </div>
                        <div class="col-md-6">
                            <label for="documento_identificacao_clt" class="form-label">Documento de Identificação:</label>
                            <input type="file" id="documento_identificacao_clt" name="documento_identificacao" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="carteira_orgao_profissional_clt" class="form-label">Carteira do Órgão Profissional:</label>
                            <input type="file" id="carteira_orgao_profissional_clt" name="carteira_orgao_profissional" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="aso_clt" class="form-label">ASO:</label>
                            <input type="file" id="aso_clt" name="aso" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="ordem_servico_clt" class="form-label">Ordem de Serviço:</label>
                            <input type="file" id="ordem_servico_clt" name="ordem_servico" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="pgr_clt" class="form-label">PGR:</label>
                            <input type="file" id="pgr_clt" name="pgr" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="pcmso_clt" class="form-label">PCMSO:</label>
                            <input type="file" id="pcmso_clt" name="pcmso" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="certificados_treinamentos_clt" class="form-label">Certificados de Treinamentos:</label>
                            <input type="file" id="certificados_treinamentos_clt" name="certificados_treinamentos" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="cautela_epi_epc_clt" class="form-label">Cautela EPI/EPC:</label>
                            <input type="file" id="cautela_epi_epc_clt" name="cautela_epi_epc" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label for="apr_pt_clt" class="form-label">APR/PT:</label>
                            <input type="file" id="apr_pt_clt" name="apr_pt" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'pessoa_juridica': `
            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">1. Dados da Empresa</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="nome_empresa_clt" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_clt" name="nome_empresa" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label for="atividade_servico_clt" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_clt" name="atividade_servico" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card shadow-sm">
                <div class="card-header"><h6 class="mb-0">Dados da Pessoa Jurídica</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Documento de Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Carteira do Órgão Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">CNPJ:</label>
                            <input type="file" name="cnpj" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Contrato de Prestação de Serviço:</label>
                            <input type="file" name="contrato_prestacao_servico" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'mei': `
            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">1. Dados da Empresa</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="nome_empresa_clt" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_clt" name="nome_empresa" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label for="atividade_servico_clt" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_clt" name="atividade_servico" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card shadow-sm">
                <div class="card-header"><h6 class="mb-0">Dados do MEI</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Documento de Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Carteira do Órgão Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Certificado MEI:</label>
                            <input type="file" name="certificado_mei" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Contrato de Prestação de Serviço:</label>
                            <input type="file" name="contrato_prestacao_servico" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'autonomo': `
            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">1. Dados da Empresa</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="nome_empresa_clt" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_clt" name="nome_empresa" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label for="atividade_servico_clt" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_clt" name="atividade_servico" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card shadow-sm">
                <div class="card-header"><h6 class="mb-0">Dados do Autônomo</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Documento de Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Carteira do Órgão Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Declaração de Autônomo:</label>
                            <input type="file" name="declaracao_autonomo" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Contrato de Prestação de Serviço:</label>
                            <input type="file" name="contrato_prestacao_servico" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'associado': `
            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">1. Dados da Empresa</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="nome_empresa_clt" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_clt" name="nome_empresa" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label for="atividade_servico_clt" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_clt" name="atividade_servico" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card shadow-sm">
                <div class="card-header"><h6 class="mb-0">Dados do Associado</h6></div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Documento de Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Carteira do Órgão Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Contrato de Associação:</label>
                            <input type="file" name="contrato_associacao" class="form-control" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `
    };
    // ==================================================================
    //             FIM DA CORREÇÃO NOS FORMULÁRIOS DINÂMICOS
    // ==================================================================

    // Função para limpar completamente o container de formulários
    function limparFormularios() {
        formsContainer.innerHTML = '';
    }

    // Função para exibir o formulário da subcategoria selecionada
    function exibirFormulario(subcategoria) {
        limparFormularios();
        if (formularios[subcategoria]) {
            formsContainer.innerHTML = formularios[subcategoria];
        }
    }

    // Event listener para mudança de categoria
    categoriaSelect.addEventListener('change', function() {
        const categoria = this.value;
        
        if (categoria === 'FORNECEDOR') {
            subcategoriaContainer.style.display = 'block';
            subcategoriaSelect.required = true;
        } else {
            subcategoriaContainer.style.display = 'none';
            subcategoriaSelect.required = false;
            subcategoriaSelect.value = '';
            limparFormularios();
        }
    });

    // Event listener para mudança de subcategoria
    subcategoriaSelect.addEventListener('change', function() {
        const subcategoria = this.value;
        
        if (subcategoria) {
            exibirFormulario(subcategoria);
        } else {
            limparFormularios();
        }
    });

    // Limpar formulários quando o modal é fechado
    const modal = document.getElementById('modalDeCadastroUnico');
    modal.addEventListener('hidden.bs.modal', function() {
        categoriaSelect.value = '';
        subcategoriaSelect.value = '';
        subcategoriaContainer.style.display = 'none';
        subcategoriaSelect.required = false;
        document.getElementById('validade_meses').value = '12';
        limparFormularios();
    });
});