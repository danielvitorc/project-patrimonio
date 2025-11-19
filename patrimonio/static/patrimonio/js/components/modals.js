// project-patrimonio/patrimonio/static/patrimonio/js/components/modals.js

document.addEventListener('DOMContentLoaded', () => {

    // Função para abrir um modal
    const openModal = (modalId) => {
        // Seleciona o overlay pelo ID
        const modalOverlay = document.getElementById(modalId);
        if (modalOverlay && modalOverlay.classList.contains('modal-overlay')) {
            modalOverlay.classList.add('active'); // Adiciona a classe para mostrar
            document.body.classList.add('modal-open'); // Opcional: Impede scroll no fundo quando o modal está aberto
            // Opcional: Focar no primeiro elemento focável dentro do modal
            const focusableElement = modalOverlay.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (focusableElement) {
                // Pequeno delay para garantir que o modal esteja visível antes de focar
                setTimeout(() => focusableElement.focus(), 50);
            }
        } else {
            console.warn(`Modal overlay with ID "${modalId}" not found or element is not a modal overlay.`);
        }
    };

    // Função para fechar um modal
    const closeModal = (modalOverlay) => {
        if (modalOverlay && modalOverlay.classList.contains('modal-overlay')) {
            modalOverlay.classList.remove('active'); // Remove a classe para esconder
            document.body.classList.remove('modal-open'); // Restaura scroll no fundo
        } else {
            console.warn("Attempted to close an element that is not a modal overlay:", modalOverlay);
        }
    };

    // --- Event Listeners ---

    // 1. Adiciona listener para botões/links que ABREM modais
    //    Procura por elementos com o atributo 'data-modal-target'
    document.body.addEventListener('click', (event) => {
        // Encontra o elemento clicado ou um de seus pais que tenha o atributo
        const trigger = event.target.closest('[data-modal-target]');
        if (trigger) {
            event.preventDefault(); // Previne comportamento padrão (ex: seguir um link '#')
            const modalId = trigger.getAttribute('data-modal-target'); // Pega o valor (ex: '#meuModalOverlay')
            if (modalId && modalId.startsWith('#')) {
                openModal(modalId.substring(1)); // Chama openModal com o ID sem o '#'
            } else {
                console.warn(`Invalid data-modal-target value: "${modalId}". It should start with '#'.`);
            }
        }
    });

    // 2. Adiciona listener para elementos que FECHAM modais
    //    Procura por cliques em elementos com 'data-modal-dismiss' OU diretamente no overlay
    document.body.addEventListener('click', (event) => {
        // Verifica se o clique foi num botão de fechar
        const dismissTrigger = event.target.closest('[data-modal-dismiss]');
        // Verifica se o clique foi diretamente no fundo (overlay)
        const isOverlayClick = event.target.classList.contains('modal-overlay');

        if (dismissTrigger || isOverlayClick) {
            // Encontra o elemento .modal-overlay mais próximo (pai) do elemento clicado
            const modalOverlay = event.target.closest('.modal-overlay');
            if (modalOverlay) {
                closeModal(modalOverlay); // Chama closeModal com o overlay encontrado
            }
        }
    });

    // 3. Adiciona listener para fechar o modal ativo com a tecla ESC
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            // Encontra o último modal que está visível (com a classe 'active')
            const activeModal = document.querySelector('.modal-overlay.active');
            if (activeModal) {
                closeModal(activeModal); // Fecha o modal ativo
            }
        }
    });

}); // Fim do DOMContentLoaded