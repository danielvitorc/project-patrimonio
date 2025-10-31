// project-patrimonio/patrimonio/static/patrimonio/js/modal_cadastro_dinamico.js
// Refatorado para usar classes CSS customizadas (sem Bootstrap)

document.addEventListener('DOMContentLoaded', function() {
    // ID atualizado para o overlay que definiremos no HTML
    const modal = document.getElementById('modalDeCadastroUnicoOverlay'); 
    if (!modal) {
        // console.warn("Modal de cadastro dinâmico não encontrado nesta página.");
        return; // Sai se o modal não estiver nesta página
    }

    const categoriaSelect = modal.querySelector('#categoria');
    const subcategoriaSelect = modal.querySelector('#subcategoria');
    const subcategoriaContainer = modal.querySelector('#subcategoria-container');
    const formsContainer = modal.querySelector('#forms-container');

    // ==================================================================
    //           INÍCIO DO HTML REFATORADO (SEM BOOTSTRAP)
    // ==================================================================
    const formularios = {
        'trabalhador_clt': `
            <div class="card-form-section">
                <h3 class="card-form-title">1. Dados da Empresa</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group grid-col-span-2">
                            <label for="nome_empresa_clt" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_clt" name="nome_empresa" class="form-input" required>
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label for="atividade_servico_clt" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_clt" name="atividade_servico" class="form-input">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-form-section">
                <h3 class="card-form-title">2. Dados do Trabalhador CLT</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="nome_representante_clt" class="form-label">Nome do Representante:</label>
                            <input type="text" id="nome_representante_clt" name="nome_representante" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label for="descricao_cargo_clt" class="form-label">Descrição do Cargo:</label>
                            <input type="text" id="descricao_cargo_clt" name="descricao_cargo" class="form-input">
                        </div>
                        <div class="form-group">
                            <label for="documento_identificacao_clt" class="form-label">Doc. Identificação:</label>
                            <input type="file" id="documento_identificacao_clt" name="documento_identificacao" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="carteira_orgao_profissional_clt" class="form-label">Carteira Profissional:</label>
                            <input type="file" id="carteira_orgao_profissional_clt" name="carteira_orgao_profissional" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="aso_clt" class="form-label">ASO:</label>
                            <input type="file" id="aso_clt" name="aso" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="ordem_servico_clt" class="form-label">Ordem de Serviço:</label>
                            <input type="file" id="ordem_servico_clt" name="ordem_servico" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="pgr_clt" class="form-label">PGR:</label>
                            <input type="file" id="pgr_clt" name="pgr" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="pcmso_clt" class="form-label">PCMSO:</label>
                            <input type="file" id="pcmso_clt" name="pcmso" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="certificados_treinamentos_clt" class="form-label">Certificados:</label>
                            <input type="file" id="certificados_treinamentos_clt" name="certificados_treinamentos" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="cautela_epi_epc_clt" class="form-label">Cautela EPI/EPC:</label>
                            <input type="file" id="cautela_epi_epc_clt" name="cautela_epi_epc" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label for="apr_pt_clt" class="form-label">APR/PT:</label>
                            <input type="file" id="apr_pt_clt" name="apr_pt" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'pessoa_juridica': `
            <div class="card-form-section">
                <h3 class="card-form-title">1. Dados da Empresa</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group grid-col-span-2">
                            <label for="nome_empresa_pj" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_pj" name="nome_empresa" class="form-input" required>
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label for="atividade_servico_pj" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_pj" name="atividade_servico" class="form-input">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-form-section">
                <h3 class="card-form-title">2. Dados da Pessoa Jurídica</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Doc. Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Carteira Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">CNPJ:</label>
                            <input type="file" name="cnpj" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label class="form-label">Contrato de Prestação de Serviço:</label>
                            <input type="file" name="contrato_prestacao_servico" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'mei': `
            <div class="card-form-section">
                <h3 class="card-form-title">1. Dados da Empresa</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group grid-col-span-2">
                            <label for="nome_empresa_mei" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_mei" name="nome_empresa" class="form-input" required>
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label for="atividade_servico_mei" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_mei" name="atividade_servico" class="form-input">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-form-section">
                <h3 class="card-form-title">2. Dados do MEI</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Doc. Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Carteira Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Certificado MEI:</label>
                            <input type="file" name="certificado_mei" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label class="form-label">Contrato de Prestação de Serviço:</label>
                            <input type="file" name="contrato_prestacao_servico" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'autonomo': `
            <div class="card-form-section">
                <h3 class="card-form-title">1. Dados da Empresa</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group grid-col-span-2">
                            <label for="nome_empresa_autonomo" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_autonomo" name="nome_empresa" class="form-input" required>
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label for="atividade_servico_autonomo" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_autonomo" name="atividade_servico" class="form-input">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-form-section">
                <h3 class="card-form-title">2. Dados do Autônomo</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Doc. Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Carteira Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Declaração de Autônomo:</label>
                            <input type="file" name="declaracao_autonomo" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label class="form-label">Contrato de Prestação de Serviço:</label>
                            <input type="file" name="contrato_prestacao_servico" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `,
        'associado': `
            <div class="card-form-section">
                <h3 class="card-form-title">1. Dados da Empresa</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group grid-col-span-2">
                            <label for="nome_empresa_associado" class="form-label">Nome da Empresa:</label>
                            <input type="text" id="nome_empresa_associado" name="nome_empresa" class="form-input" required>
                        </div>
                        <div class="form-group grid-col-span-2">
                            <label for="atividade_servico_associado" class="form-label">Atividade/Serviço:</label>
                            <input type="text" id="atividade_servico_associado" name="atividade_servico" class="form-input">
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-form-section">
                <h3 class="card-form-title">2. Dados do Associado</h3>
                <div class="card-form-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Nome do Representante:</label>
                            <input type="text" name="nome_representante" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Doc. Identificação:</label>
                            <input type="file" name="documento_identificacao" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Carteira Profissional:</label>
                            <input type="file" name="carteira_orgao_profissional" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Contrato de Associação:</label>
                            <input type="file" name="contrato_associacao" class="form-input" accept=".pdf,.jpg,.jpeg,.png">
                        </div>
                    </div>
                </div>
            </div>
        `
    };
    // ==================================================================
    //             FIM DO HTML REFATORADO
    // ==================================================================


    // Função para limpar completamente o container de formulários
    function limparFormularios() {
        if (formsContainer) formsContainer.innerHTML = '';
    }

    // Função para exibir o formulário da subcategoria selecionada
    function exibirFormulario(subcategoria) {
        limparFormularios();
        if (formsContainer && formularios[subcategoria]) {
            formsContainer.innerHTML = formularios[subcategoria];
            // Aplica estilos de forms.css aos novos inputs
            // (Não é mais necessário se as classes .form-input, .form-label
            // já estão no HTML e no forms.css)
        }
    }

    // Event listener para mudança de categoria
    if (categoriaSelect) {
        categoriaSelect.addEventListener('change', function() {
            const categoria = this.value;
            
            if (categoria === 'FORNECEDOR') {
                if(subcategoriaContainer) subcategoriaContainer.style.display = 'block';
                if(subcategoriaSelect) subcategoriaSelect.required = true;
            } else {
                if(subcategoriaContainer) subcategoriaContainer.style.display = 'none';
                if(subcategoriaSelect) {
                    subcategoriaSelect.required = false;
                    subcategoriaSelect.value = '';
                }
                limparFormularios();
            }
        });
    }

    // Event listener para mudança de subcategoria
    if (subcategoriaSelect) {
        subcategoriaSelect.addEventListener('change', function() {
            const subcategoria = this.value;
            
            if (subcategoria) {
                exibirFormulario(subcategoria);
            } else {
                limparFormularios();
            }
        });
    }

    // Limpar formulários quando o modal é fechado (usando observador, já que modals.js controla)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class' && !modal.classList.contains('active')) {
                // Modal foi fechado
                if(categoriaSelect) categoriaSelect.value = '';
                if(subcategoriaSelect) subcategoriaSelect.value = '';
                if(subcategoriaContainer) subcategoriaContainer.style.display = 'none';
                if(subcategoriaSelect) subcategoriaSelect.required = false;
                limparFormularios();
            }
        });
    });
    observer.observe(modal, { attributes: true });

});