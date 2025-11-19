
// project-patrimonio/patrimonio/static/patrimonio/js/integracao.js
// Refatorado para remover jQuery e Bootstrap, e usar modals.js

document.addEventListener('DOMContentLoaded', () => {

    // Helper: Função para pegar o CSRF token
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
    // As variáveis globais window.csrfToken e window.gerarLinkUrl
    // devem ser definidas no template HTML (bloco extra_js)
    const csrfToken = window.csrfToken || getCookie('csrftoken');


    // Armazena o ID do fornecedor quando o modal de validade é aberto
    let currentFornecedorId = null;

    // Listener global para capturar cliques em botões
    // Isso funciona mesmo que a tabela seja recarregada dinamicamente.
    document.body.addEventListener('click', (e) => {
        
        // Gatilho 1: Usuário clicou no botão para ABRIR o modal de validade
        // (Ex: <button data-modal-target="#modalValidadeOverlay..." data-id="123">)
        const trigger = e.target.closest('[data-modal-target^="#modalValidadeOverlay"]');
        if (trigger) {
            // Guarda o ID do fornecedor que estamos prestes a processar
            currentFornecedorId = trigger.getAttribute('data-id');
        }

        // Gatilho 2: Usuário clicou no botão "Gerar Link" DENTRO do modal de validade
        // (Ex: <button class="btn-confirmar-link">)
        const confirmButton = e.target.closest('.btn-confirmar-link');
        if (confirmButton) {
            e.preventDefault();
            
            if (!currentFornecedorId) {
                console.error("ID do Fornecedor não encontrado. O clique no gatilho 1 falhou?");
                return;
            }

            const modalValidade = confirmButton.closest('.modal-overlay');
            if (!modalValidade) {
                console.error("Não foi possível encontrar o modal-overlay pai.");
                return;
            }

            const validadeInput = modalValidade.querySelector('input[name="validade_meses"]');
            const validade = validadeInput ? validadeInput.value : '12'; // Default 12

            if (!validade) {
                alert("Informe a validade em meses!");
                return;
            }

            // Fecha o modal de validade (função do modals.js)
            modalValidade.classList.remove('active');

            // Prepara a URL (garante que termine com /)
            const url = window.gerarLinkUrl.replace('0/', `${currentFornecedorId}/`);
            // Substitui o $.ajax pelo fetch
            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({ validade_meses: validade })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ${response.status}: Falha na requisição`);
                }
                return response.json();
            })
            .then(response => {
                if (response.erro) {
                    alert(response.erro);
                    return;
                }
                
                // Preenche os campos no modal de "Link Gerado"
                const tokenEl = document.getElementById('tokenGerado');
                const linkEl = document.getElementById('linkGerado');
                
                if(tokenEl) tokenEl.value = response.token;
                if(linkEl) {
                    linkEl.textContent = response.link;
                    linkEl.href = response.link;
                }

                // Abre o modal de "Link Gerado" (função do modals.js)
                // (O ID do overlay foi renomeado no HTML que sugeri)
                const modalLinkGerado = document.getElementById('modalLinkGeradoOverlay');
                if (modalLinkGerado) {
                    modalLinkGerado.classList.add('active');
                } else {
                    console.error("Modal #modalLinkGeradoOverlay não encontrado.");
                }
            })
            .catch(error => {
                console.error("Erro ao gerar link:", error);
                alert("Ocorreu um erro ao gerar o link.");
            });
        }
    });
    // Fim do listener global de cliques
    // --- Lógica do Modal de Foto Expandida ---
    const modalFoto = document.getElementById('modalFotoOverlay');
    const fotoExpandida = document.getElementById('fotoExpandida');

    if (modalFoto && fotoExpandida) {
        // Usamos delegação de eventos no body para pegar cliques em fotos da tabela
        document.body.addEventListener('click', function(event) {
            // Procura pelo elemento que aciona o modal da foto
            const triggerElement = event.target.closest('[data-modal-target="#modalFotoOverlay"]');

            if (triggerElement) {
                // Pega a URL do atributo data-foto
                const urlFoto = triggerElement.getAttribute('data-foto');
                if (urlFoto) {
                    // Define o 'src' da imagem grande dentro do modal
                    fotoExpandida.src = urlFoto;
                } else {
                    // Limpa se não houver foto (ex: placeholder)
                    fotoExpandida.src = ""; 
                }
                // A abertura do modal em si é tratada pelo modals.js
            }
        });
    }
    // ===================================================================
    //         FIM DO BLOCO ADICIONADO
    // ===================================================================

});