// project-patrimonio/patrimonio/static/patrimonio/js/sidebar.js

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('appSidebar');
    const toggleButton = document.getElementById('sidebarToggleBtn');
    const overlay = document.getElementById('sidebarOverlay');
    const mainContent = document.querySelector('.main-content'); // Ajuste seletor se necessário
    const sidebarStateKey = 'sidebarCollapsed'; // Chave para localStorage

    // --- Funções Auxiliares ---
    const isMobile = () => window.innerWidth <= 992;

    const applySidebarState = (isCollapsed) => {
        if (!sidebar) return;

        if (isMobile()) {
            // Em mobile, 'collapsed' significa 'fechada' (transform)
            if (isCollapsed) {
                sidebar.classList.remove('active'); // Esconde
                if (overlay) overlay.classList.remove('active'); // Esconde overlay
            } else {
                sidebar.classList.add('active'); // Mostra
                if (overlay) overlay.classList.add('active'); // Mostra overlay
            }
            // Remove a classe 'collapsed' em mobile para garantir largura total
            sidebar.classList.remove('collapsed');
            if (toggleButton) toggleButton.setAttribute('aria-expanded', !isCollapsed);

        } else {
            // Em desktop, 'collapsed' controla a largura
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
            }
             // Garante que a classe 'active' não esteja presente em desktop
            sidebar.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            if (toggleButton) toggleButton.setAttribute('aria-expanded', !isCollapsed);

            // Salva o estado em desktop
            try {
                localStorage.setItem(sidebarStateKey, isCollapsed ? 'true' : 'false');
            } catch (e) {
                console.warn("Não foi possível salvar o estado da sidebar no localStorage.");
            }
        }
    };

    const toggleSidebar = () => {
        if (!sidebar) return;
        let shouldBeCollapsed;
        if (isMobile()) {
            // Em mobile, o toggle inverte a classe 'active'
            shouldBeCollapsed = sidebar.classList.contains('active'); // Se está ativa, deve ser recolhida (escondida)
        } else {
            // Em desktop, o toggle inverte a classe 'collapsed'
            shouldBeCollapsed = !sidebar.classList.contains('collapsed');
        }
        applySidebarState(shouldBeCollapsed);
    };

    // --- Inicialização ---
    if (sidebar && toggleButton) {
        // Verifica estado salvo ou padrão (começa expandida em desktop)
        let initialStateCollapsed = false;
        if (!isMobile()) {
             try {
                initialStateCollapsed = localStorage.getItem(sidebarStateKey) === 'true';
            } catch (e) {
                 initialStateCollapsed = false; // Default se localStorage falhar
            }
        } else {
             initialStateCollapsed = true; // Começa fechada em mobile
        }


        applySidebarState(initialStateCollapsed); // Aplica estado inicial

        // Evento de clique no botão toggle
        toggleButton.addEventListener('click', toggleSidebar);

        // Evento de clique no overlay (para fechar em mobile)
        if (overlay) {
            overlay.addEventListener('click', () => {
                if (isMobile()) {
                    applySidebarState(true); // Fecha a sidebar
                }
            });
        }

        // Reavalia o estado ao redimensionar a janela
        window.addEventListener('resize', () => {
            let currentStateCollapsed = false;
             try {
                currentStateCollapsed = localStorage.getItem(sidebarStateKey) === 'true';
             } catch(e) {
                 currentStateCollapsed = false;
             }

             // Se redimensionar para mobile, sempre fecha. Se para desktop, usa o estado salvo.
            applySidebarState(isMobile() ? true : currentStateCollapsed);
        });

    } else {
        console.warn('Sidebar ou botão de toggle não encontrado no DOM.');
    }


}); // Fim do DOMContentLoaded