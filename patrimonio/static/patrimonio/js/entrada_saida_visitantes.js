// project-patrimonio/patrimonio/static/patrimonio/js/entrada_saida_visitantes.js

document.addEventListener("DOMContentLoaded", function () {

    // --- Lógica da Webcam (baseada no script inline original) ---
    let webcamStarted = false;
    let webcamStream = null;

    const modalCadastro = document.getElementById('modalCadastroFornecedorOverlay'); // ID atualizado
    const videoElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('canvas');
    const fotoInput = document.getElementById('id_foto_visitante');
    const galeriaFoto = document.getElementById('galeria-foto-visitante');
    const imagemPreview = document.getElementById('imagem-preview-visitante');
    const btnTirarFoto = document.getElementById('btn-tirar-foto');
    const btnRetomarWebcam = document.getElementById('btn-retomar-webcam');
    const webcamStatus = document.getElementById('webcam-status');
    const categoriaSelect = document.getElementById('id_categoria');
    const visitanteFields = document.getElementById('visitanteFields');

    function updateWebcamStatus(statusText, isError = false) {
        if (!webcamStatus) return;
        webcamStatus.textContent = statusText;
        // Classes de tema serão tratadas pelo CSS
        webcamStatus.className = 'webcam-status-badge'; 
        if (isError) {
            webcamStatus.classList.add('status-error');
        } else if (statusText === 'Webcam Ativa') {
            webcamStatus.classList.add('status-success');
        } else {
            webcamStatus.classList.add('status-info');
        }
    }

    function startWebcam() {
        if (webcamStarted || !videoElement) return;
        updateWebcamStatus('Iniciando Webcam...', false);
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                videoElement.srcObject = stream;
                webcamStream = stream;
                webcamStarted = true;
                videoElement.style.display = 'block';
                if (btnTirarFoto) btnTirarFoto.style.display = 'block';
                if (btnRetomarWebcam) btnRetomarWebcam.style.display = 'none';
                updateWebcamStatus('Webcam Ativa', false);
            })
            .catch(err => {
                console.error("Erro ao acessar webcam visitante:", err);
                updateWebcamStatus('Erro ao iniciar Webcam', true);
                videoElement.style.display = 'none';
                if (btnTirarFoto) btnTirarFoto.style.display = 'none';
                if (btnRetomarWebcam) btnRetomarWebcam.style.display = 'block';
            });
    }

    function pararWebcam() {
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
            webcamStarted = false;
            videoElement.srcObject = null;
            videoElement.style.display = 'none';
            if (btnTirarFoto) btnTirarFoto.style.display = 'none';
            updateWebcamStatus('Webcam Inativa', false);
        }
    }

    function retomarWebcam() {
        if (galeriaFoto) galeriaFoto.style.display = 'none';
        if (fotoInput) fotoInput.value = '';
        if (imagemPreview) imagemPreview.src = '';
        startWebcam();
    }

    function tirarFoto() {
        if (!canvasElement || !videoElement || !fotoInput || !imagemPreview || !galeriaFoto) return;
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        canvasElement.getContext('2d').drawImage(videoElement, 0, 0);

        const imageData = canvasElement.toDataURL('image/jpeg');
        fotoInput.value = imageData;
        imagemPreview.src = imageData;
        galeriaFoto.style.display = 'block';

        pararWebcam();
        if (btnRetomarWebcam) btnRetomarWebcam.style.display = 'block';
        updateWebcamStatus('Foto Capturada', false);
    }

    function removerFotoVisitante() {
        if (fotoInput) fotoInput.value = '';
        if (imagemPreview) imagemPreview.src = '';
        if (galeriaFoto) galeriaFoto.style.display = 'none';
        if (btnRetomarWebcam) btnRetomarWebcam.style.display = 'none';
        startWebcam(); // reativa a câmera
    }

    // Adiciona listeners aos botões da webcam (se existirem)
    if (btnTirarFoto) btnTirarFoto.addEventListener('click', tirarFoto);
    if (btnRetomarWebcam) btnRetomarWebcam.addEventListener('click', retomarWebcam);
    const btnRemoverFoto = document.getElementById('btn-remover-foto'); // ID novo no HTML refatorado
    if (btnRemoverFoto) btnRemoverFoto.addEventListener('click', removerFotoVisitante);

    // Lógica para mostrar/esconder webcam baseada no <select>
    function toggleWebcamFields() {
        if (!categoriaSelect || !visitanteFields) return;
        const selected = categoriaSelect.value;
        if (selected === 'VISITANTE') {
            visitanteFields.style.display = 'block';
            startWebcam();
        } else {
            visitanteFields.style.display = 'none';
            pararWebcam();
        }
    }
    if (categoriaSelect) {
        categoriaSelect.addEventListener("change", toggleWebcamFields);
    }

    // Lógica para ligar/desligar webcam ao abrir/fechar modal de cadastro
    if (modalCadastro) {
        // Observador para quando o modal é aberto/fechado (via classe 'active')
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'class') {
                    const isActive = modalCadastro.classList.contains('active');
                    if (isActive) {
                        // Modal foi aberto
                        toggleWebcamFields();
                    } else {
                        // Modal foi fechado
                        pararWebcam();
                        if (fotoInput) fotoInput.value = '';
                        if (imagemPreview) imagemPreview.src = '';
                        if (galeriaFoto) galeriaFoto.style.display = 'none';
                        if (btnRetomarWebcam) btnRetomarWebcam.style.display = 'none';
                        updateWebcamStatus('Webcam Inativa', false);
                    }
                }
            });
        });
        observer.observe(modalCadastro, { attributes: true });
    }


    // --- Lógica do Modal de Foto Expandida ---
    const modalFoto = document.getElementById('modalFotoOverlay'); // ID atualizado
    const fotoExpandida = document.getElementById('fotoExpandida');
    if (modalFoto && fotoExpandida) {
        // Usamos delegação de eventos no body para pegar cliques em fotos
        document.body.addEventListener('click', function(event) {
            const triggerElement = event.target.closest('[data-modal-target="#modalFotoOverlay"]');
            if (triggerElement) {
                const urlFoto = triggerElement.getAttribute('data-foto');
                if (urlFoto) {
                    fotoExpandida.src = urlFoto;
                    // Abertura do modal é tratada pelo modals.js
                }
            }
        });
    }

    // --- Lógica de Filtro da Tabela de Entradas ---
    const filtroData = document.getElementById('filtro-data');
    const filtroCategoria = document.getElementById('filtro-categoria');
    const filtroFornecedor = document.getElementById('filtro-fornecedor');
    const filtroResponsavel = document.getElementById('filtro-responsavel');
    const filtroStatus = document.getElementById('filtro-status');
    const tabelaEntradasBody = document.getElementById('tabela-entradas-body');
    const linhasEntradas = tabelaEntradasBody ? tabelaEntradasBody.querySelectorAll('tr') : [];

    function normalizeString(str) {
        return str ? str.trim().toLowerCase() : "";
    }

    function filtrarTabelaEntradas() {
        if (!tabelaEntradasBody) return;

        const valData = filtroData ? filtroData.value : ""; // yyyy-mm-dd
        const valCategoria = normalizeString(filtroCategoria ? filtroCategoria.value : "");
        const valFornecedor = normalizeString(filtroFornecedor ? filtroFornecedor.value : "");
        const valResponsavel = normalizeString(filtroResponsavel ? filtroResponsavel.value : "");
        const valStatus = normalizeString(filtroStatus ? filtroStatus.value : "");

        for (let row of linhasEntradas) {
            if (row.children.length < 9) continue; // Pula linhas de "vazio"

            const celData = row.cells[1].innerText; // "dd/mm/yyyy"
            const celCategoria = normalizeString(row.cells[5].innerText);
            const celFornecedor = normalizeString(row.cells[6].innerText);
            const celResponsavel = normalizeString(row.cells[7].innerText);
            const celStatus = normalizeString(row.cells[8].innerText);

            // Converter data da célula para yyyy-mm-dd
            const parts = celData.split('/');
            const dataFormatada = parts.length === 3 ? `${parts[2]}-${parts[1].padStart(2,'0')}-${parts[0].padStart(2,'0')}` : '';

            const passaData = !valData || dataFormatada === valData;
            const passaCategoria = !valCategoria || celCategoria.includes(valCategoria);
            const passaFornecedor = !valFornecedor || celFornecedor.includes(valFornecedor);
            const passaResponsavel = !valResponsavel || celResponsavel.includes(valResponsavel);
            const passaStatus = !valStatus || celStatus.includes(valStatus);

            row.style.display = (passaData && passaCategoria && passaFornecedor && passaResponsavel && passaStatus) ? '' : 'none';
        }
    }

    // Adiciona eventos aos filtros
    [filtroData, filtroCategoria, filtroFornecedor, filtroResponsavel, filtroStatus].forEach(input => {
        if (input) {
            input.addEventListener('input', filtrarTabelaEntradas);
            input.addEventListener('change', filtrarTabelaEntradas);
        }
    });

});