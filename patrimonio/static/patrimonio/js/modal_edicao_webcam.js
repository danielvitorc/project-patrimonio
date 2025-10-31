// project-patrimonio/patrimonio/static/patrimonio/js/modal_edicao_webcam.js
// Refatorado para remover jQuery e Bootstrap JS.

// ===================================================================
// ESCOPO GLOBAL DO SCRIPT
// ===================================================================

// Variáveis de stream da Webcam
let webcamVisitanteStream = null;
let webcamRepresentanteStream = null;

// Helper: Pega o CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrfToken = getCookie('csrftoken');

// ===================================================================
// FUNÇÕES DE CONTROLE DA WEBCAM
// (Abstraídas para aceitar seletores)
// ===================================================================

/**
 * Inicia uma stream de webcam
 * @param {HTMLVideoElement} videoEl - O elemento <video>
 * @param {HTMLSpanElement} statusEl - O span de status
 * @param {HTMLButtonElement} btnCapturar - O botão de capturar
 * @param {HTMLButtonElement} btnParar - O botão de parar
 * @returns {Promise<MediaStream>} - A stream
 */
async function iniciarWebcam(videoEl, statusEl, btnCapturar, btnParar) {
    if (!videoEl || !statusEl || !btnCapturar || !btnParar) return null;
    if (videoEl.srcObject) return videoEl.srcObject; // Já está ativa

    statusEl.textContent = "Iniciando...";
    statusEl.className = 'webcam-status-badge status-info';
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: { ideal: 640 }, height: { ideal: 480 } } 
        });
        videoEl.srcObject = stream;
        videoEl.style.display = "block";
        btnCapturar.style.display = "inline-flex";
        btnParar.style.display = "inline-flex";
        statusEl.textContent = "Webcam Ativa";
        statusEl.className = 'webcam-status-badge status-success';
        return stream;
    } catch (err) {
        console.error("Erro ao acessar webcam:", err);
        statusEl.textContent = "Erro na Câmera";
        statusEl.className = 'webcam-status-badge status-error';
        return null;
    }
}

/**
 * Captura uma foto da stream
 * @param {MediaStream} stream - A stream da webcam
 * @param {HTMLVideoElement} videoEl - O elemento <video>
 * @param {HTMLCanvasElement} canvasEl - O elemento <canvas>
 * @param {HTMLInputElement} inputEl - O <input type="hidden">
 * @param {HTMLElement} previewEl - O container <div> do preview
 * @param {HTMLImageElement} imgPreviewEl - A <img> de preview
 */
function capturarFoto(stream, videoEl, canvasEl, inputEl, previewEl, imgPreviewEl) {
    if (!stream || !videoEl || !canvasEl || !inputEl || !previewEl || !imgPreviewEl) return;
    
    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
    canvasEl.getContext("2d").drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
    
    const imageData = canvasEl.toDataURL("image/jpeg", 0.8);
    inputEl.value = imageData;
    imgPreviewEl.src = imageData;
    previewEl.style.display = "block";
    
    // Para a webcam após a captura
    pararWebcam(stream, videoEl, null, null, null); // Passa null para os que não precisamos
}

/**
 * Para uma stream de webcam
 * @param {MediaStream} stream - A stream
 * @param {HTMLVideoElement} videoEl - O elemento <video>
 * @param {HTMLSpanElement} statusEl - O span de status
 * @param {HTMLButtonElement} btnCapturar - O botão de capturar
 * @param {HTMLButtonElement} btnParar - O botão de parar
 * @returns {null} - Retorna null para zerar a variável de stream
 */
function pararWebcam(stream, videoEl, statusEl, btnCapturar, btnParar) {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    if (videoEl) videoEl.style.display = "none";
    if (statusEl) {
        statusEl.textContent = "Inativa";
        statusEl.className = 'webcam-status-badge status-info';
    }
    if (btnCapturar) btnCapturar.style.display = "none";
    if (btnParar) btnParar.style.display = "none";
    return null; // Retorna null para a variável de stream ser resetada
}

/**
 * Limpa a foto capturada
 * @param {HTMLInputElement} inputEl - O <input type="hidden">
 * @param {HTMLElement} previewEl - O container <div> do preview
 * @param {HTMLImageElement} imgPreviewEl - A <img> de preview
 */
function removerFoto(inputEl, previewEl, imgPreviewEl) {
    if (!inputEl || !previewEl || !imgPreviewEl) return;
    inputEl.value = "";
    imgPreviewEl.src = "";
    previewEl.style.display = "none";
}

// ===================================================================
// FUNÇÕES DE CONTROLE DO MODAL DE EDIÇÃO
// ===================================================================

/**
 * Mostra/Esconde campos do formulário com base na categoria/subcategoria
 */
function mostrarCamposCategoriaEdicao() {
    const categoria = document.getElementById("categoria_edicao")?.value;
    const subcategoria = document.getElementById("subcategoria_edicao")?.value;

    // Esconde todos os containers
    document.getElementById("campos_visitante_edicao")?.style.setProperty('display', 'none');
    document.getElementById("campos_fornecedor_edicao")?.style.setProperty('display', 'none');
    document.getElementById("campos_representante_edicao")?.style.setProperty('display', 'none');
    document.getElementById("subcategoria_container_edicao")?.style.setProperty('display', 'none');
    
    // Esconde todos os sub-campos
    document.querySelectorAll('.sub-fields').forEach(el => el.style.setProperty('display', 'none'));

    // Mostra baseado na Categoria
    if (categoria === "VISITANTE") {
        document.getElementById("campos_visitante_edicao")?.style.setProperty('display', 'block');
    } else if (categoria === "FORNECEDOR") {
        document.getElementById("subcategoria_container_edicao")?.style.setProperty('display', 'block');
        document.getElementById("campos_fornecedor_edicao")?.style.setProperty('display', 'block');
        document.getElementById("campos_representante_edicao")?.style.setProperty('display', 'block');

        // Mostra sub-campo baseado na Subcategoria
        if (subcategoria) {
            const subCampoEl = document.getElementById(`campos_${subcategoria.toLowerCase()}_edicao`);
            if (subCampoEl) {
                subCampoEl.style.setProperty('display', 'block');
            }
        }
    }
}

/**
 * Preenche os campos do formulário com os dados carregados do 'data.dados'
 */
function inicializarCamposModalEdicao(data) {
    const dados = data.dados;
    if (!dados) return;

    // Preenche campos básicos
    document.getElementById("categoria_edicao").value = dados.categoria || "";
    document.getElementById("subcategoria_edicao").value = dados.subcategoria || "";
    document.getElementById("validade_meses_edicao").value = dados.validade_meses || "";
    document.getElementById("status_edicao").value = dados.status || "";
    
    // Preenche campos de Visitante
    if (dados.categoria === "VISITANTE" && dados.visitante) {
        document.getElementById("nome_visitante_edicao").value = dados.visitante.nome || "";
        document.getElementById("documento_visitante_edicao").value = dados.visitante.documento || "";
        document.getElementById("motivo_visita_edicao").value = dados.visitante.motivo_visita || "";
        if (dados.visitante.foto_visitante) {
            document.getElementById("img-preview-visitante-edicao").src = dados.visitante.foto_visitante;
            document.getElementById("preview-foto-visitante-edicao").style.display = "block";
        }
    }
    
    // Preenche campos de Fornecedor
    if (dados.categoria === "FORNECEDOR") {
        if (dados.fornecedor_servico) {
            document.getElementById("nome_empresa_edicao").value = dados.fornecedor_servico.nome_empresa || "";
            document.getElementById("atividade_servico_edicao").value = dados.fornecedor_servico.atividade_servico || "";
        }
        if (dados.trabalhador_relacionado) {
            document.getElementById("nome_representante_edicao").value = dados.trabalhador_relacionado.nome_representante || "";
            if (dados.trabalhador_relacionado.foto_representante) {
                document.getElementById("img-preview-representante-edicao").src = dados.trabalhador_relacionado.foto_representante;
                document.getElementById("preview-foto-representante-edicao").style.display = "block";
            }
            // Preenche sub-campos
            if (dados.subcategoria === "CLT") {
                document.getElementById("descricao_cargo_edicao").value = dados.trabalhador_relacionado.descricao_cargo || "";
            }
            // ... (adicionar preenchimento para outros campos de subcategoria se necessário) ...
        }
    }
    
    // Mostra os campos corretos
    mostrarCamposCategoriaEdicao();
    
    // Adiciona listener para o select de subcategoria
    // (O select de categoria é 'disabled', então não precisa de listener)
    document.getElementById("subcategoria_edicao").addEventListener("change", mostrarCamposCategoriaEdicao);
    
    // Adiciona listeners aos botões da webcam
    adicionarListenersWebcam();
}

/**
 * Adiciona todos os event listeners para as webcams no modal de edição
 */
function adicionarListenersWebcam() {
    // --- Webcam Visitante ---
    const visVideo = document.getElementById("webcam-visitante-edicao");
    const visStatus = document.getElementById("webcam-status-visitante");
    const visCanvas = document.getElementById("canvas-visitante-edicao");
    const visInput = document.getElementById("foto_visitante_base64_edicao");
    const visPreview = document.getElementById("preview-foto-visitante-edicao");
    const visImgPreview = document.getElementById("img-preview-visitante-edicao");
    const visBtnIniciar = document.getElementById("btn-iniciar-visitante");
    const visBtnCapturar = document.getElementById("btn-capturar-visitante");
    const visBtnParar = document.getElementById("btn-parar-visitante");
    const visBtnRemover = document.getElementById("btn-remover-visitante");

    visBtnIniciar?.addEventListener('click', async () => {
        webcamVisitanteStream = await iniciarWebcam(visVideo, visStatus, visBtnCapturar, visBtnParar);
    });
    visBtnCapturar?.addEventListener('click', () => {
        capturarFoto(webcamVisitanteStream, visVideo, visCanvas, visInput, visPreview, visImgPreview);
        webcamVisitanteStream = pararWebcam(webcamVisitanteStream, visVideo, visStatus, visBtnCapturar, visBtnParar);
    });
    visBtnParar?.addEventListener('click', () => {
        webcamVisitanteStream = pararWebcam(webcamVisitanteStream, visVideo, visStatus, visBtnCapturar, visBtnParar);
    });
    visBtnRemover?.addEventListener('click', () => {
        removerFoto(visInput, visPreview, visImgPreview);
    });

    // --- Webcam Representante ---
    const repVideo = document.getElementById("webcam-representante-edicao");
    const repStatus = document.getElementById("webcam-status-representante");
    const repCanvas = document.getElementById("canvas-representante-edicao");
    const repInput = document.getElementById("foto_representante_base64_edicao");
    const repPreview = document.getElementById("preview-foto-representante-edicao");
    const repImgPreview = document.getElementById("img-preview-representante-edicao");
    const repBtnIniciar = document.getElementById("btn-iniciar-representante");
    const repBtnCapturar = document.getElementById("btn-capturar-representante");
    const repBtnParar = document.getElementById("btn-parar-representante");
    const repBtnRemover = document.getElementById("btn-remover-representante");
    
    repBtnIniciar?.addEventListener('click', async () => {
        webcamRepresentanteStream = await iniciarWebcam(repVideo, repStatus, repBtnCapturar, repBtnParar);
    });
    repBtnCapturar?.addEventListener('click', () => {
        capturarFoto(webcamRepresentanteStream, repVideo, repCanvas, repInput, repPreview, repImgPreview);
        webcamRepresentanteStream = pararWebcam(webcamRepresentanteStream, repVideo, repStatus, repBtnCapturar, repBtnParar);
    });
    repBtnParar?.addEventListener('click', () => {
        webcamRepresentanteStream = pararWebcam(webcamRepresentanteStream, repVideo, repStatus, repBtnCapturar, repBtnParar);
    });
    repBtnRemover?.addEventListener('click', () => {
        removerFoto(repInput, repPreview, repImgPreview);
    });
}

// ===================================================================
// EVENT LISTENERS PRINCIPAIS (nível do documento)
// ===================================================================

document.addEventListener('DOMContentLoaded', () => {
    const modalEditar = document.getElementById('modalEditarFornecedorOverlay');
    if (!modalEditar) {
         // console.warn("Modal de edição não encontrado nesta página.");
         return; // Sai se o modal principal não existir
    }
    
    let currentEditId = null; // Armazena o ID do fornecedor sendo editado
    const modalBody = modalEditar.querySelector('#modal-body-content');

    // Função para carregar o conteúdo do modal
    const carregarDadosFornecedor = (fornecedorId) => {
        if (!modalBody) return;
        modalBody.innerHTML = `<p class="loading-text">Carregando dados...</p>`; // Estado de loading

        fetch(`/fornecedor/${fornecedorId}/dados/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    modalBody.innerHTML = data.form_html; // Injeta o HTML
                    // Agora que o HTML existe, inicializa os campos e a lógica
                    inicializarCamposModalEdicao(data);
                } else {
                     modalBody.innerHTML = `<p style="color: var(--danger-color);">Erro: ${data.error}</p>`;
                }
            })
            .catch(error => {
                console.error("Erro na requisição AJAX:", error);
                 modalBody.innerHTML = `<p style="color: var(--danger-color);">Ocorreu um erro ao carregar os dados.</p>`;
            });
    };

    // Observa o modal de edição para carregar o conteúdo quando ele for aberto
    // e parar as webcams quando for fechado.
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                const isActive = modalEditar.classList.contains('active');
                if (isActive) {
                    // Modal foi aberto
                    // Precisamos saber qual botão foi clicado.
                    // Usamos um truque: o listener 'click' abaixo adiciona a classe 'active-trigger'
                    const editTrigger = document.querySelector('.active-trigger[data-modal-target="#modalEditarFornecedorOverlay"]');
                    if (editTrigger) {
                        currentEditId = editTrigger.getAttribute('data-id');
                        if (currentEditId) {
                            // Atualiza a action do formulário (que será carregado)
                            // O form ID é 'formEditarFornecedor'
                            // (A action será setada no listener de submit)
                            carregarDadosFornecedor(currentEditId);
                        }
                        editTrigger.classList.remove('active-trigger'); // Limpa o gatilho
                    }
                } else {
                    // Modal foi fechado
                    webcamVisitanteStream = pararWebcam(webcamVisitanteStream, document.getElementById("webcam-visitante-edicao"), document.getElementById("webcam-status-visitante"), document.getElementById("btn-capturar-visitante"), document.getElementById("btn-parar-visitante"));
                    webcamRepresentanteStream = pararWebcam(webcamRepresentanteStream, document.getElementById("webcam-representante-edicao"), document.getElementById("webcam-status-representante"), document.getElementById("btn-capturar-representante"), document.getElementById("btn-parar-representante"));
                    if (modalBody) modalBody.innerHTML = ""; // Limpa o conteúdo
                }
            }
        });
    });
    observer.observe(modalEditar, { attributes: true });

    // Delegação de eventos para todo o 'body'
    document.body.addEventListener('click', (e) => {
        // 1. Marca qual botão abriu o modal de edição
        const trigger = e.target.closest('[data-modal-target="#modalEditarFornecedorOverlay"]');
        if (trigger) {
            // Remove 'active-trigger' de qualquer outro botão
            document.querySelectorAll('.active-trigger').forEach(btn => btn.classList.remove('active-trigger'));
            // Adiciona ao botão clicado
            trigger.classList.add('active-trigger');
        }
    });
    
    // 2. Listener para o SUBMIT do formulário de edição (delegado ao modal)
    modalEditar.addEventListener('submit', (e) => {
        const form = e.target.closest('#formEditarFornecedor');
        if (!form) return; // Não é o submit que procuramos
        
        e.preventDefault();
        if (!currentEditId) {
            alert("Erro: ID do fornecedor não definido.");
            return;
        }

        const formData = new FormData(form);
        const actionUrl = `/fornecedor/${currentEditId}/editar/`; // Constrói a URL de submit

        fetch(actionUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken,
                "Accept": "application/json" // Pede JSON de volta
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Fornecedor atualizado com sucesso!");
                location.reload(); // Recarregar a página para mostrar as alterações
            } else {
                alert("Erro ao atualizar fornecedor: " + (data.error || "Erro desconhecido"));
                // Se a view retornar form_html com erros, podemos re-injetá-lo
                if (data.form_html) {
                    if (modalBody) {
                        modalBody.innerHTML = data.form_html;
                        // Re-inicializar campos após re-renderização do formulário com erros
                        inicializarCamposModalEdicao(data); // 'data' contém 'data.dados'
                    }
                }
            }
        })
        .catch(error => {
            console.error("Erro no fetch:", error);
            alert("Erro ao processar solicitação.");
        });
    });
});