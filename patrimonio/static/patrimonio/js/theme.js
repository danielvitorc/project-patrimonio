// project-patrimonio/patrimonio/static/patrimonio/js/theme.js
// VERSÃO REFATORADA E GLOBAL

/**
 * Função GLOBAL para aplicar o tema e atualizar os ícones.
 * Pode ser chamada por outros scripts.
 * @param {string} theme - 'light' or 'dark'
 */
function applyTheme(theme) {
    if (theme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    // Salva a preferência no localStorage
    localStorage.setItem('theme', theme); 

    // Atualiza TODOS os botões de tema na página (seja na sidebar ou login)
    const allToggleButtons = document.querySelectorAll('.theme-toggle-button');
    allToggleButtons.forEach(button => {
        const sunIcon = button.querySelector('.fa-sun');
        const moonIcon = button.querySelector('.fa-moon');
        if (sunIcon && moonIcon) {
            if (theme === 'light') {
                sunIcon.style.display = 'none';
                moonIcon.style.display = 'inline-block';
            } else {
                sunIcon.style.display = 'inline-block';
                moonIcon.style.display = 'none';
            }
        }
    });

    // Atualiza o fundo do canvas de estrelas (específico do login)
    const starsCanvas = document.getElementById('stars');
    if (starsCanvas) {
        if (theme === 'light') {
            starsCanvas.style.backgroundColor = 'var(--light-secondary-bg)';
        } else {
            starsCanvas.style.backgroundColor = 'var(--dark-secondary-bg)';
        }
    }
}

// --- Executa ao carregar o DOM ---
document.addEventListener('DOMContentLoaded', () => {

    // 1. Aplica o tema inicial
    // Verifica tema salvo ou preferência do sistema
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const currentTheme = savedTheme ? savedTheme : (prefersDark ? 'dark' : 'light');
    // Aplica o tema inicial e atualiza os ícones
    applyTheme(currentTheme); 

    // 2. Adiciona evento a TODOS os botões de tema (pela classe)
    // Isso funciona no login E na sidebar
    const allToggleButtons = document.querySelectorAll('.theme-toggle-button');
    allToggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Pega o tema atual e inverte
            const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    });
    // 4. Lógica para auto-esconder mensagens (toasts)
    const allMessages = document.querySelectorAll('.message-item');
    allMessages.forEach((message, index) => {
        // 5 segundos para a primeira mensagem, 5.5s para a segunda, etc.
        const delay = 5000 + (index * 500); 

        setTimeout(() => {
            // Adiciona a classe que dispara a animação CSS
            message.classList.add('fading-out');

            // Remove o elemento do DOM após a transição
            // (O tempo da transição é 500ms, definido no base.css)
            setTimeout(() => {
                message.remove();
            }, 550); // 50ms de buffer
        }, delay);
    });
    // 3. Ouve mudanças na preferência do sistema (opcional, mas bom)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        // Só muda se o usuário não definiu manualmente um tema
        if (!localStorage.getItem('theme')) { 
            applyTheme(event.matches ? 'dark' : 'light');
        }
    });
});