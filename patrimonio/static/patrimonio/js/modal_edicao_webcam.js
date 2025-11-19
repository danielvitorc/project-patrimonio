// project-patrimonio/patrimonio/static/patrimonio/js/modal_edicao_webcam.js
// Refatorado para remover jQuery, Bootstrap JS, e usar o sistema de modal customizado.

// ===================================================================
// ESCOPO GLOBAL DO SCRIPT
// ===================================================================

// Variáveis de stream da Webcam
let webcamVisitanteEdicaoStream = null;
let webcamRepresentanteEdicaoStream = null;
let currentEditId = null; // Armazena o ID do fornecedor sendo editado

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
// Usa a variável global definida no HTML (preferencial) ou pega do cookie
const csrfToken = window.csrfToken || getCookie('csrftoken'); 

// ===================================================================
// FUNÇÕES DE CONTROLE DA WEBCAM (Abstraídas)
// ===================================================================

/**
 * Inicia uma stream de webcam
 * @param {HTMLVideoElement} videoEl - O elemento <video>
 * @param {HTMLSpanElement} statusEl - O span de status
 * @param {HTMLButtonElement} btnCapturar - O botão de capturar
 * @param {HTMLButtonElement} btnParar - O botão de parar
 * @returns {Promise<MediaStream | null>} - A stream
 */
async function iniciarWebcam(videoEl, statusEl, btnCapturar, btnParar) {
    if (!videoEl || !statusEl || !btnCapturar || !btnParar) {
        console.warn("Elementos da webcam faltando.");
        return null;
    }
    
    // Para qualquer stream anterior (caso haja)
    if (videoEl.srcObject) {
        videoEl.srcObject.getTracks().forEach(track => track.stop());
    }

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
 * @param {HTMLVideoElement} videoEl - O elemento <video>
 * @param {HTMLCanvasElement} canvasEl - O elemento <canvas>
 * @param {HTMLInputElement} inputEl - O <input type="hidden">
 * @param {HTMLElement} previewEl - O container <div> do preview
 * @param {HTMLImageElement} imgPreviewEl - A <img> de preview
 */
function capturarFoto(videoEl, canvasEl, inputEl, previewEl, imgPreviewEl) {
    if (!videoEl || !canvasEl || !inputEl || !previewEl || !imgPreviewEl) {
         console.warn("Elementos de captura de foto faltando.");
         return;
    }
    
    if (!videoEl.videoWidth) {
        console.warn("Webcam não está pronta para capturar (videoWidth=0).");
        return;
    }

    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
    canvasEl.getContext("2d").drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
    
    const imageData = canvasEl.toDataURL("image/jpeg", 0.8);
    inputEl.value = imageData;
    imgPreviewEl.src = imageData;
    previewEl.style.display = "block";
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
    // Seleciona os elementos dentro do modal de edição
    const modal = document.getElementById('modalEditarFornecedorOverlay');
    if (!modal) return;

    const categoria = modal.querySelector("#categoria_edicao")?.value;
    const subcategoria = modal.querySelector("#subcategoria_edicao")?.value;

    // Esconde todos os containers
    modal.querySelector("#campos_visitante_edicao")?.style.setProperty('display', 'none');
    modal.querySelector("#campos_fornecedor_edicao")?.style.setProperty('display', 'none');
    modal.querySelector("#campos_representante_edicao")?.style.setProperty('display', 'none');
    modal.querySelector("#subcategoria_container_edicao")?.style.setProperty('display', 'none');
    
    // Esconde todos os sub-campos
    modal.querySelectorAll('.sub-fields').forEach(el => el.style.setProperty('display', 'none'));

    // Mostra baseado na Categoria
    if (categoria === "VISITANTE") {
        modal.querySelector("#campos_visitante_edicao")?.style.setProperty('display', 'block');
    } else if (categoria === "FORNECEDOR") {
        modal.querySelector("#subcategoria_container_edicao")?.style.setProperty('display', 'block');
        modal.querySelector("#campos_fornecedor_edicao")?.style.setProperty('display', 'block');
        modal.querySelector("#campos_representante_edicao")?.style.setProperty('display', 'block');

        // Mostra sub-campo baseado na Subcategoria
        if (subcategoria) {
            const subCampoEl = modal.querySelector(`#campos_${subcategoria.toLowerCase()}_edicao`);
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
    const modal = document.getElementById('modalEditarFornecedorOverlay');
    if (!modal || !data.dados) {
        console.error("Falha ao inicializar campos: modal ou 'data.dados' não encontrados.");
        return;
    }

    const dados = data.dados;

    // Preenche campos básicos
    const selCategoria = modal.querySelector("#categoria_edicao");
    const selSubcategoria = modal.querySelector("#subcategoria_edicao");
    const inputValidade = modal.querySelector("#validade_meses_edicao");
    const selStatus = modal.querySelector("#status_edicao");

    if (selCategoria) selCategoria.value = dados.categoria || "";
    if (selSubcategoria) selSubcategoria.value = dados.subcategoria || "";
    if (inputValidade) inputValidade.value = dados.validade_meses || "";
    if (selStatus) selStatus.value = dados.status || "";
    
    // Preenche campos de Visitante
    if (dados.categoria === "VISITANTE" && dados.visitante) {
        modal.querySelector("#nome_visitante_edicao").value = dados.visitante.nome || "";
        modal.querySelector("#documento_visitante_edicao").value = dados.visitante.documento || "";
        modal.querySelector("#motivo_visita_edicao").value = dados.visitante.motivo_visita || "";
        if (dados.visitante.foto_visitante) {
            modal.querySelector("#img-preview-visitante-edicao").src = dados.visitante.foto_visitante;
            modal.querySelector("#preview-foto-visitante-edicao").style.display = "block";
        }
    }
    
    // Preenche campos de Fornecedor
    if (dados.categoria === "FORNECEDOR") {
        if (dados.fornecedor_servico) {
            modal.querySelector("#nome_empresa_edicao").value = dados.fornecedor_servico.nome_empresa || "";
            modal.querySelector("#atividade_servico_edicao").value = dados.fornecedor_servico.atividade_servico || "";
        }
        if (dados.trabalhador_relacionado) {
            modal.querySelector("#nome_representante_edicao").value = dados.trabalhador_relacionado.nome_representante || "";
            if (dados.trabalhador_relacionado.foto_representante) {
                modal.querySelector("#img-preview-representante-edicao").src = dados.trabalhador_relacionado.foto_representante;
                modal.querySelector("#preview-foto-representante-edicao").style.display = "block";
            }
            if (dados.subcategoria === "CLT" && dados.trabalhador_relacionado.descricao_cargo) {
                modal.querySelector("#descricao_cargo_edicao").value = dados.trabalhador_relacionado.descricao_cargo;
            }
            // ... (adicionar preenchimento para outros campos de subcategoria se necessário) ...
        }
    }
    
    // Mostra os campos corretos
    mostrarCamposCategoriaEdicao();
    
    // Adiciona listener para o select de subcategoria (se ele for habilitado no futuro)
    if (selSubcategoria) {
        selSubcategoria.addEventListener("change", mostrarCamposCategoriaEdicao);
    }
    
    // Adiciona listeners aos botões da webcam
    adicionarListenersWebcam();
}

/**
 * Adiciona todos os event listeners para as webcams no modal de edição
 * Esta função é chamada DEPOIS que o HTML é injetado.
 */
function adicionarListenersWebcam() {
    const modal = document.getElementById('modalEditarFornecedorOverlay');
    if (!modal) return;

    // --- Webcam Visitante ---
    const visVideo = modal.querySelector("#webcam-visitante-edicao");
    const visStatus = modal.querySelector("#webcam-status-visitante");
    const visCanvas = modal.querySelector("#canvas-visitante-edicao");
    const visInput = modal.querySelector("#foto_visitante_base64_edicao");
    const visPreview = modal.querySelector("#preview-foto-visitante-edicao");
    const visImgPreview = modal.querySelector("#img-preview-visitante-edicao");
    const visBtnIniciar = modal.querySelector("#btn-iniciar-visitante-edicao");
    const visBtnCapturar = modal.querySelector("#btn-capturar-visitante-edicao");
    const visBtnParar = modal.querySelector("#btn-parar-visitante-edicao");
    const visBtnRemover = modal.querySelector("#btn-remover-visitante-edicao");

    visBtnIniciar?.addEventListener('click', async () => {
        webcamVisitanteEdicaoStream = await iniciarWebcam(visVideo, visStatus, visBtnCapturar, visBtnParar);
    });
    visBtnCapturar?.addEventListener('click', () => {
        capturarFoto(visVideo, visCanvas, visInput, visPreview, visImgPreview);
        webcamVisitanteEdicaoStream = pararWebcam(webcamVisitanteEdicaoStream, visVideo, visStatus, visBtnCapturar, visBtnParar);
    });
    visBtnParar?.addEventListener('click', () => {
        webcamVisitanteEdicaoStream = pararWebcam(webcamVisitanteEdicaoStream, visVideo, visStatus, visBtnCapturar, visBtnParar);
    });
    visBtnRemover?.addEventListener('click', () => {
        removerFoto(visInput, visPreview, visImgPreview);
    });

    // --- Webcam Representante ---
    const repVideo = modal.querySelector("#webcam-representante-edicao");
    const repStatus = modal.querySelector("#webcam-status-representante");
    const repCanvas = modal.querySelector("#canvas-representante-edicao");
    const repInput = modal.querySelector("#foto_representante_base64_edicao");
    const repPreview = modal.querySelector("#preview-foto-representante-edicao");
    const repImgPreview = modal.querySelector("#img-preview-representante-edicao");
    const repBtnIniciar = modal.querySelector("#btn-iniciar-representante-edicao");
    const repBtnCapturar = modal.querySelector("#btn-capturar-representante-edicao");
    const repBtnParar = modal.querySelector("#btn-parar-representante-edicao");
    const repBtnRemover = modal.querySelector("#btn-remover-representante-edicao");
    
    repBtnIniciar?.addEventListener('click', async () => {
        webcamRepresentanteEdicaoStream = await iniciarWebcam(repVideo, repStatus, repBtnCapturar, repBtnParar);
    });
    repBtnCapturar?.addEventListener('click', () => {
        capturarFoto(repVideo, repCanvas, repInput, repPreview, repImgPreview);
        webcamRepresentanteEdicaoStream = pararWebcam(webcamRepresentanteEdicaoStream, repVideo, repStatus, repBtnCapturar, repBtnParar);
    });
    repBtnParar?.addEventListener('click', () => {
        webcamRepresentanteEdicaoStream = pararWebcam(webcamRepresentanteEdicaoStream, repVideo, repStatus, repBtnCapturar, repBtnParar);
    });
    repBtnRemover?.addEventListener('click', () => {
        removerFoto(repInput, repPreview, repImgPreview);
    });
}

// ===================================================================
// EVENT LISTENERS PRINCIPAIS (Carregados quando a página abre)
// ===================================================================

document.addEventListener('DOMContentLoaded', () => {
    const modalEditar = document.getElementById('modalEditarFornecedorOverlay');
    if (!modalEditar) {
         // console.warn("Modal de edição não encontrado nesta página.");
         return; // Sai se o modal principal não existir
    }
    
    const modalBodyWrapper = modalEditar.querySelector('#modal-body-content-wrapper'); // Wrapper do body
    if (!modalBodyWrapper) {
         console.error("#modal-body-content-wrapper não encontrado!");
         return;
    }

    // Função para carregar o conteúdo do modal
    const carregarDadosFornecedor = (fornecedorId) => {
        modalBodyWrapper.innerHTML = `<div class="modal-body"><p style="text-align: center; padding: 2rem; color: var(--dark-disabled);">Carregando dados...</p></div>`; // Estado de loading

        // URL para buscar o HTML do formulário de edição
        const url = `/fornecedor/${fornecedorId}/dados/`;

        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`Erro ${response.status} ao buscar dados.`);
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    modalBodyWrapper.innerHTML = data.form_html; // Injeta o HTML (que agora contém o <form>)
                    // Agora que o HTML existe, inicializa os campos e a lógica
                    inicializarCamposModalEdicao(data);
                } else {
                     modalBodyWrapper.innerHTML = `<div class="modal-body"><p style="color: var(--danger-color);">Erro: ${data.error}</p></div>`;
                }
            })
            .catch(error => {
                console.error("Erro na requisição AJAX:", error);
                 modalBodyWrapper.innerHTML = `<div class="modal-body"><p style="color: var(--danger-color);">Ocorreu um erro ao carregar os dados.</p></div>`;
            });
    };

    // Observa o modal de edição para carregar o conteúdo quando ele for aberto
    // e parar as webcams quando for fechado.
    // Isso substitui os eventos 'show.bs.modal' e 'hide.bs.modal'
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
                        currentEditId = editTrigger.getAttribute('data-id'); // Pega o ID do fornecedor
                        if (currentEditId) {
                            carregarDadosFornecedor(currentEditId);
                        }
                        editTrigger.classList.remove('active-trigger'); // Limpa o gatilho
                    }
                } else {
                    // Modal foi fechado
                    // Para as duas webcams
                    webcamVisitanteEdicaoStream = pararWebcam(
                        webcamVisitanteEdicaoStream, 
                        modalEditar.querySelector("#webcam-visitante-edicao"), 
                        modalEditar.querySelector("#webcam-status-visitante"), 
                        modalEditar.querySelector("#btn-capturar-visitante-edicao"), 
                        modalEditar.querySelector("#btn-parar-visitante-edicao")
                    );
                    webcamRepresentanteEdicaoStream = pararWebcam(
                        webcamRepresentanteEdicaoStream, 
                        modalEditar.querySelector("#webcam-representante-edicao"), 
                        modalEditar.querySelector("#webcam-status-representante"), 
                        modalEditar.querySelector("#btn-capturar-representante-edicao"), 
                        modalEditar.querySelector("#btn-parar-representante-edicao")
                    );
                    // Limpa o conteúdo para a próxima abertura
                    modalBodyWrapper.innerHTML = `<div class="modal-body"><p style="text-align: center; padding: 2rem; color: var(--dark-disabled);">Carregando...</p></div>`;
                    currentEditId = null; // Reseta o ID
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
    // Isso substitui o $('#formEditarFornecedor').on('submit', ...)
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
                alert("Erro ao atualizar: " + (data.error || "Verifique os campos."));
                // Se a view retornar form_html com erros, podemos re-injetá-lo
                if (data.form_html) {
                    if (modalBodyWrapper) {
                        modalBodyWrapper.innerHTML = data.form_html;
                        // Re-inicializar campos após re-renderização do formulário com erros
                        inicializarCamposModalEdicao(data); // 'data' contém 'data.dados'
                    }
                }
            }
        })
        .catch(error => {
            console.error("Erro no fetch:", error);
            alert("Erro ao processar solicitação. Tente novamente.");
        });
    });
});