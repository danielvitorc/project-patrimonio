// Variáveis globais para controle das webcams
let webcamVisitanteStream = null;
let webcamRepresentanteStream = null;
let webcamVisitanteAtiva = false;
let webcamRepresentanteAtiva = false;

// ==================== FUNÇÕES PARA WEBCAM DO VISITANTE ====================

function iniciarWebcamVisitante() {
    if (webcamVisitanteAtiva) return;
    
    const video = document.getElementById("webcam-visitante-edicao");
    const btnCapturar = document.getElementById("btn-capturar-visitante");
    const btnParar = document.getElementById("btn-parar-visitante");
    
    if (!video) { 
        console.warn("Elemento webcam-visitante-edicao não encontrado.");
        return;
    }

    navigator.mediaDevices.getUserMedia({ 
        video: { 
            width: { ideal: 640 }, 
            height: { ideal: 480 } 
        } 
    })
    .then(stream => {
        video.srcObject = stream;
        video.style.display = "block";
        webcamVisitanteStream = stream;
        webcamVisitanteAtiva = true;
        
        // Mostrar botões de controle
        if (btnCapturar) btnCapturar.style.display = "inline-block"; 
        if (btnParar) btnParar.style.display = "inline-block"; 
        
        console.log("Webcam do visitante iniciada com sucesso");
    })
    .catch(err => {
        console.error("Erro ao acessar webcam do visitante:", err);
        alert("Erro ao acessar a câmera. Verifique as permissões do navegador.");
    });
}

function capturarFotoVisitante() {
    const video = document.getElementById("webcam-visitante-edicao");
    const canvas = document.getElementById("canvas-visitante-edicao");
    const input = document.getElementById("foto_visitante_base64_edicao");
    const preview = document.getElementById("preview-foto-visitante-edicao");
    const imgPreview = document.getElementById("img-preview-visitante-edicao");
    
    if (!video || !canvas || !input || !preview || !imgPreview) { 
        console.warn("Elementos da captura de foto do visitante não encontrados.");
        return;
    }

    if (!webcamVisitanteAtiva || !video.videoWidth) {
        alert("Câmera não está ativa ou não carregou completamente.");
        return;
    }
    
    // Configurar canvas com as dimensões do vídeo
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Desenhar frame atual do vídeo no canvas
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Converter para base64
    const imageData = canvas.toDataURL("image/jpeg", 0.8);
    
    // Salvar no campo hidden
    input.value = imageData;
    
    // Mostrar preview
    imgPreview.src = imageData;
    preview.style.display = "block";
    
    // Parar webcam após captura
    pararWebcamVisitante();
    
    console.log("Foto do visitante capturada com sucesso");
}

function pararWebcamVisitante() {
    if (webcamVisitanteStream) {
        webcamVisitanteStream.getTracks().forEach(track => track.stop());
        webcamVisitanteStream = null;
    }
    
    const video = document.getElementById("webcam-visitante-edicao");
    const btnCapturar = document.getElementById("btn-capturar-visitante");
    const btnParar = document.getElementById("btn-parar-visitante");
    
    if (video) { 
        video.style.display = "none";
        video.srcObject = null;
    }
    webcamVisitanteAtiva = false;
    
    // Esconder botões de controle
    if (btnCapturar) btnCapturar.style.display = "none"; 
    if (btnParar) btnParar.style.display = "none"; 
    
    console.log("Webcam do visitante parada");
}

function removerFotoVisitante() {
    const input = document.getElementById("foto_visitante_base64_edicao");
    const preview = document.getElementById("preview-foto-visitante-edicao");
    const imgPreview = document.getElementById("img-preview-visitante-edicao");
    
    if (!input || !preview || !imgPreview) { 
        console.warn("Elementos de remoção de foto do visitante não encontrados.");
        return;
    }

    input.value = "";
    imgPreview.src = "";
    preview.style.display = "none";
    
    console.log("Foto do visitante removida");
}

// ==================== FUNÇÕES PARA WEBCAM DO REPRESENTANTE ====================

function iniciarWebcamRepresentante() {
    if (webcamRepresentanteAtiva) return;
    
    const video = document.getElementById("webcam-representante-edicao");
    const btnCapturar = document.getElementById("btn-capturar-representante");
    const btnParar = document.getElementById("btn-parar-representante");
    
    if (!video) { 
        console.warn("Elemento webcam-representante-edicao não encontrado.");
        return;
    }

    navigator.mediaDevices.getUserMedia({ 
        video: { 
            width: { ideal: 640 }, 
            height: { ideal: 480 } 
        } 
    })
    .then(stream => {
        video.srcObject = stream;
        video.style.display = "block";
        webcamRepresentanteStream = stream;
        webcamRepresentanteAtiva = true;
        
        // Mostrar botões de controle
        if (btnCapturar) btnCapturar.style.display = "inline-block"; 
        if (btnParar) btnParar.style.display = "inline-block"; 
        
        console.log("Webcam do representante iniciada com sucesso");
    })
    .catch(err => {
        console.error("Erro ao acessar webcam do representante:", err);
        alert("Erro ao acessar a câmera. Verifique as permissões do navegador.");
    });
}

function capturarFotoRepresentante() {
    const video = document.getElementById("webcam-representante-edicao");
    const canvas = document.getElementById("canvas-representante-edicao");
    const input = document.getElementById("foto_representante_base64_edicao");
    const preview = document.getElementById("preview-foto-representante-edicao");
    const imgPreview = document.getElementById("img-preview-representante-edicao");
    
    if (!video || !canvas || !input || !preview || !imgPreview) { 
        console.warn("Elementos da captura de foto do representante não encontrados.");
        return;
    }

    if (!webcamRepresentanteAtiva || !video.videoWidth) {
        alert("Câmera não está ativa ou não carregou completamente.");
        return;
    }
    
    // Configurar canvas com as dimensões do vídeo
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Desenhar frame atual do vídeo no canvas
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Converter para base64
    const imageData = canvas.toDataURL("image/jpeg", 0.8);
    
    // Salvar no campo hidden
    input.value = imageData;
    
    // Mostrar preview
    imgPreview.src = imageData;
    preview.style.display = "block";
    
    // Parar webcam após captura
    pararWebcamRepresentante();
    
    console.log("Foto do representante capturada com sucesso");
}

function pararWebcamRepresentante() {
    if (webcamRepresentanteStream) {
        webcamRepresentanteStream.getTracks().forEach(track => track.stop());
        webcamRepresentanteStream = null;
    }
    
    const video = document.getElementById("webcam-representante-edicao");
    const btnCapturar = document.getElementById("btn-capturar-representante");
    const btnParar = document.getElementById("btn-parar-representante");
    
    if (video) { 
        video.style.display = "none";
        video.srcObject = null;
    }
    webcamRepresentanteAtiva = false;
    
    // Esconder botões de controle
    if (btnCapturar) btnCapturar.style.display = "none"; 
    if (btnParar) btnParar.style.display = "none"; 
    
    console.log("Webcam do representante parada");
}

function removerFotoRepresentante() {
    const input = document.getElementById("foto_representante_base64_edicao");
    const preview = document.getElementById("preview-foto-representante-edicao");
    const imgPreview = document.getElementById("img-preview-representante-edicao");
    
    if (!input || !preview || !imgPreview) { 
        console.warn("Elementos de remoção de foto do representante não encontrados.");
        return;
    }

    input.value = "";
    imgPreview.src = "";
    preview.style.display = "none";
    
    console.log("Foto do representante removida");
}

// ==================== FUNÇÕES DE CONTROLE DO MODAL ====================

// Esta função agora será chamada APÓS o HTML do formulário ser carregado no modal
function inicializarCamposModal(data) {
    const dados = data.dados; // Os dados do fornecedor

    // Preencher campos básicos
    const categoriaEdicao = document.getElementById("categoria_edicao");
    const subcategoriaEdicao = document.getElementById("subcategoria_edicao");
    const validadeMesesEdicao = document.getElementById("validade_meses_edicao");
    const statusEdicao = document.getElementById("status_edicao");

    if (categoriaEdicao) categoriaEdicao.value = dados.categoria;
    if (subcategoriaEdicao) subcategoriaEdicao.value = dados.subcategoria || "";
    if (validadeMesesEdicao) validadeMesesEdicao.value = dados.validade_meses;
    if (statusEdicao) statusEdicao.value = dados.status;
    
    // Re-atribuir event listeners para os selects de categoria e subcategoria
    if (categoriaEdicao) {
        categoriaEdicao.removeEventListener("change", mostrarCamposCategoria); // Evitar duplicação
        categoriaEdicao.addEventListener("change", mostrarCamposCategoria);
    }
    
    if (subcategoriaEdicao) {
        subcategoriaEdicao.removeEventListener("change", mostrarCamposCategoria); // Evitar duplicação
        subcategoriaEdicao.addEventListener("change", mostrarCamposCategoria);
    }

    // Mostrar campos apropriados com base nos dados carregados
    mostrarCamposCategoria();
    
    // Preencher campos específicos baseado na categoria
    if (dados.categoria === "VISITANTE" && dados.visitante) {
        const nomeVisitanteEdicao = document.getElementById("nome_visitante_edicao");
        const documentoVisitanteEdicao = document.getElementById("documento_visitante_edicao");
        const motivoVisitaEdicao = document.getElementById("motivo_visita_edicao");

        if (nomeVisitanteEdicao) nomeVisitanteEdicao.value = dados.visitante.nome || "";
        if (documentoVisitanteEdicao) documentoVisitanteEdicao.value = dados.visitante.documento || "";
        if (motivoVisitaEdicao) motivoVisitaEdicao.value = dados.visitante.motivo_visita || "";
        
        // Mostrar foto existente se houver
        if (dados.visitante.foto_visitante) {
            const imgPreview = document.getElementById("img-preview-visitante-edicao");
            const preview = document.getElementById("preview-foto-visitante-edicao");
            if (imgPreview) imgPreview.src = dados.visitante.foto_visitante;
            if (preview) preview.style.display = "block";
        }
    } else if (dados.categoria === "FORNECEDOR") {
        // Preencher dados da empresa
        if (dados.fornecedor_servico) {
            const nomeEmpresaEdicao = document.getElementById("nome_empresa_edicao");
            const atividadeServicoEdicao = document.getElementById("atividade_servico_edicao");
            if (nomeEmpresaEdicao) nomeEmpresaEdicao.value = dados.fornecedor_servico.nome_empresa || "";
            if (atividadeServicoEdicao) atividadeServicoEdicao.value = dados.fornecedor_servico.atividade_servico || "";
        }
        
        // Preencher dados do representante
        if (dados.trabalhador_relacionado) {
            const nomeRepresentanteEdicao = document.getElementById("nome_representante_edicao");
            if (nomeRepresentanteEdicao) nomeRepresentanteEdicao.value = dados.trabalhador_relacionado.nome_representante || "";
            
            // Mostrar foto existente se houver
            if (dados.trabalhador_relacionado.foto_representante) {
                const imgPreview = document.getElementById("img-preview-representante-edicao");
                const preview = document.getElementById("preview-foto-representante-edicao");
                if (imgPreview) imgPreview.src = dados.trabalhador_relacionado.foto_representante;
                if (preview) preview.style.display = "block";
            }
            
            // Preencher campos específicos da subcategoria
            if (dados.subcategoria === "CLT") {
                const descricaoCargoEdicao = document.getElementById("descricao_cargo_edicao");
                if (descricaoCargoEdicao) descricaoCargoEdicao.value = dados.trabalhador_relacionado.descricao_cargo || "";
            } else if (dados.subcategoria === "PJ") {
                // Preencher campos PJ
            } else if (dados.subcategoria === "MEI") {
                // Preencher campos MEI
            } else if (dados.subcategoria === "AUTONOMO") {
                // Preencher campos Autônomo
            } else if (dados.subcategoria === "ASSOCIADO") {
                // Preencher campos Associado
            }
        }
    }
}

function mostrarCamposCategoria() {
    const categoriaSelect = document.getElementById("categoria_edicao");
    const subcategoriaSelect = document.getElementById("subcategoria_edicao");

    if (!categoriaSelect || !subcategoriaSelect) { 
        console.warn("Elementos categoria_edicao ou subcategoria_edicao não encontrados.");
        return;
    }

    const categoria = categoriaSelect.value;
    const subcategoria = subcategoriaSelect.value;
    
    // Esconder todos os campos primeiro
    const camposVisitante = document.getElementById("campos_visitante_edicao");
    const camposFornecedor = document.getElementById("campos_fornecedor_edicao");
    const camposRepresentante = document.getElementById("campos_representante_edicao");
    const subcategoriaContainer = document.getElementById("subcategoria_container_edicao");
    
    if (camposVisitante) camposVisitante.style.display = "none";
    if (camposFornecedor) camposFornecedor.style.display = "none";
    if (camposRepresentante) camposRepresentante.style.display = "none";
    if (subcategoriaContainer) subcategoriaContainer.style.display = "none";
    
    // Esconder campos específicos de subcategoria
    const camposClt = document.getElementById("campos_clt_edicao");
    const camposPj = document.getElementById("campos_pj_edicao");
    const camposMei = document.getElementById("campos_mei_edicao");
    const camposAutonomo = document.getElementById("campos_autonomo_edicao");
    const camposAssociado = document.getElementById("campos_associado_edicao");

    if (camposClt) camposClt.style.display = "none";
    if (camposPj) camposPj.style.display = "none";
    if (camposMei) camposMei.style.display = "none";
    if (camposAutonomo) camposAutonomo.style.display = "none";
    if (camposAssociado) camposAssociado.style.display = "none";
    
    if (categoria === "VISITANTE") {
        if (camposVisitante) camposVisitante.style.display = "block";
    } else if (categoria === "FORNECEDOR") {
        if (subcategoriaContainer) subcategoriaContainer.style.display = "block";
        if (camposFornecedor) camposFornecedor.style.display = "block";
        if (camposRepresentante) camposRepresentante.style.display = "block";
        
        // Mostrar campos específicos da subcategoria
        if (subcategoria === "CLT") {
            if (camposClt) camposClt.style.display = "block";
        } else if (subcategoria === "PJ") {
            if (camposPj) camposPj.style.display = "block";
        } else if (subcategoria === "MEI") {
            if (camposMei) camposMei.style.display = "block";
        } else if (subcategoria === "AUTONOMO") {
            if (camposAutonomo) camposAutonomo.style.display = "block";
        } else if (subcategoria === "ASSOCIADO") {
            if (camposAssociado) camposAssociado.style.display = "block";
        }
    }
}

function carregarDadosFornecedor(fornecedorId) {
    fetch(`/fornecedor/${fornecedorId}/dados/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Inserir o HTML do formulário no corpo do modal
                const modalBodyContent = document.getElementById("modal-body-content");
                if (modalBodyContent) {
                    modalBodyContent.innerHTML = data.form_html;
                }

                // Agora que o HTML do formulário está na página, inicializar os campos
                inicializarCamposModal(data);

                // Abrir o modal
                // var modal = new bootstrap.Modal(document.getElementById("modalEditarFornecedor"));
                // modal.show(); // Não chamar show aqui, pois o modal já está sendo aberto pelo show.bs.modal

            } else {
                console.error("Erro ao carregar dados do fornecedor:", data.error);
                alert("Erro ao carregar dados do fornecedor." + (data.error ? ": " + data.error : ""));
            }
        })
        .catch(error => {
            console.error("Erro na requisição AJAX:", error);
            alert("Ocorreu um erro ao carregar os dados do fornecedor.");
        });
}

// ==================== EVENT LISTENERS ====================

document.addEventListener("DOMContentLoaded", function() {
    // Event listener para quando o modal for fechado
    const modal = document.getElementById("modalEditarFornecedor");
    if (modal) {
        modal.addEventListener("hide.bs.modal", function() {
            // Parar todas as webcams quando o modal for fechado
            pararWebcamVisitante();
            pararWebcamRepresentante();
            
            // Limpar previews
            removerFotoVisitante();
            removerFotoRepresentante();
            
            // Limpar o conteúdo do modal-body-content para evitar dados antigos
            const modalBodyContent = document.getElementById("modal-body-content");
            if (modalBodyContent) {
                modalBodyContent.innerHTML = "<p>Carregando dados...</p>";
            }
            
            console.log("Modal fechado - webcams paradas e dados limpos");
        });
        
        // Event listener para quando o modal for aberto
        modal.addEventListener("show.bs.modal", function(event) {
            const button = event.relatedTarget;
            if (button) {
                const fornecedorId = button.getAttribute("data-id");
                
                // *** INÍCIO DA CORREÇÃO ***
                const form = document.getElementById("formEditarFornecedor");
                if (fornecedorId && form) {
                    // Constrói a URL correta para a view de edição
                    const actionUrl = `/fornecedor/${fornecedorId}/editar/`; // Ajuste a URL se for diferente
                    form.setAttribute("action", actionUrl);
                    
                    // Agora carrega os dados
                    carregarDadosFornecedor(fornecedorId);
                }
                // *** FIM DA CORREÇÃO ***

            } else { 
                console.warn("Modal aberto sem relatedTarget. Assumindo que o carregamento de dados já foi tratado.");
            }
        });
    }
    
    // Event listener para submit do formulário (agora que o formulário é carregado dinamicamente, este listener precisa ser re-atribuído ou usar delegação)
    // A delegação é mais robusta para elementos carregados dinamicamente
    $(document).on("submit", "#formEditarFornecedor", function(e) {
        e.preventDefault();
        let form = $(this);
        
        // Aqui você pode adicionar validações adicionais se necessário
        if (!validarFormulario()) {
            return; // Impede a submissão se a validação falhar
        }
        
        const formData = new FormData(form[0]); // Use form[0] para obter o elemento DOM nativo
        
        fetch(form.attr("action") || window.location.href, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Fornecedor atualizado com sucesso!");
                location.reload(); // Recarregar a página para mostrar as alterações
            } else {
                alert("Erro ao atualizar fornecedor: " + (data.error || "Erro desconhecido"));
                // Se a view retornar form_html com erros, você pode inseri-lo novamente
                if (data.form_html) {
                    const modalBodyContent = document.getElementById("modal-body-content");
                    if (modalBodyContent) {
                        modalBodyContent.innerHTML = data.form_html;
                        // Re-inicializar campos após re-renderização do formulário com erros
                        inicializarCamposModal(data); // Pode precisar de ajustes para lidar com erros de validação
                    }
                }
            }
        })
        .catch(error => {
            console.error("Erro:", error);
            alert("Erro ao processar solicitação.");
        });
    });
});

// ==================== FUNÇÕES AUXILIARES ====================

function validarFormulario() {
    const categoriaSelect = document.getElementById("categoria_edicao");
    if (!categoriaSelect) return true; // Se o elemento não existe, não valida

    const categoria = categoriaSelect.value;
    
    if (categoria === "VISITANTE") {
        const nome = document.getElementById("nome_visitante_edicao");
        if (nome && !nome.value.trim()) {
            alert("Nome do visitante é obrigatório.");
            return false;
        }
    } else if (categoria === "FORNECEDOR") {
        const subcategoriaSelect = document.getElementById("subcategoria_edicao");
        const nomeRepresentante = document.getElementById("nome_representante_edicao");

        if (nomeRepresentante && !nomeRepresentante.value.trim()) {
            alert("Nome do representante é obrigatório.");
            return false;
        }
        
        if (subcategoriaSelect) {
            const subcategoria = subcategoriaSelect.value;
            if (subcategoria === "CLT") {
                const descricaoCargo = document.getElementById("descricao_cargo_edicao");
                if (descricaoCargo && !descricaoCargo.value.trim()) {
                    alert("Descrição do cargo é obrigatória para CLT.");
                    return false;
                }
            } else if (subcategoria === "PJ") {
                // Adicionar validações para PJ
            } else if (subcategoria === "MEI") {
                // Adicionar validações para MEI
            } else if (subcategoria === "AUTONOMO") {
                // Adicionar validações para Autônomo
            } else if (subcategoria === "ASSOCIADO") {
                // Adicionar validações para Associado
            }
        }
    }
    return true;
}

