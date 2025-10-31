// project-patrimonio/patrimonio/static/patrimonio/js/theme.js

document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle-login'); // ID do botão na tela de login
    const sunIcon = themeToggleButton ? themeToggleButton.querySelector('.fa-sun') : null;
    const moonIcon = themeToggleButton ? themeToggleButton.querySelector('.fa-moon') : null;
    const starsCanvas = document.getElementById('stars'); // Pega o canvas

    // Função para aplicar o tema
    const applyTheme = (theme) => {
        if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            if (sunIcon) sunIcon.style.display = 'none';
            if (moonIcon) moonIcon.style.display = 'inline-block';
            if (starsCanvas) starsCanvas.style.backgroundColor = 'var(--light-secondary-bg)'; // Fundo claro para estrelas
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (sunIcon) sunIcon.style.display = 'inline-block';
            if (moonIcon) moonIcon.style.display = 'none';
            if (starsCanvas) starsCanvas.style.backgroundColor = 'var(--dark-secondary-bg)'; // Fundo escuro para estrelas
        }
        localStorage.setItem('theme', theme); // Salva a preferência
    };

    // --- Lógica do Botão Mostrar/Ocultar Senha ---
    const togglePasswordButton = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    const eyeIcon = togglePasswordButton ? togglePasswordButton.querySelector('.fa-eye') : null;
    const eyeSlashIcon = togglePasswordButton ? togglePasswordButton.querySelector('.fa-eye-slash') : null;

    if (togglePasswordButton && passwordInput && eyeIcon && eyeSlashIcon) {
        togglePasswordButton.addEventListener('click', () => {
            // Verifica o tipo atual do input
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            // Alterna os ícones
            if (type === 'password') {
                eyeIcon.style.display = 'none';
                eyeSlashIcon.style.display = 'inline-block';
                togglePasswordButton.setAttribute('aria-label', 'Mostrar senha');
            } else {
                eyeIcon.style.display = 'inline-block';
                eyeSlashIcon.style.display = 'none';
                togglePasswordButton.setAttribute('aria-label', 'Ocultar senha');
            }
        });
    }

    // Verifica tema salvo ou preferência do sistema
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const currentTheme = savedTheme ? savedTheme : (prefersDark ? 'dark' : 'light');

    // Aplica o tema inicial
    applyTheme(currentTheme);

    // Adiciona evento ao botão de toggle
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }

    // Ouve mudanças na preferência do sistema (opcional, mas bom)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        if (!localStorage.getItem('theme')) { // Só muda se o usuário não definiu manualmente
            applyTheme(event.matches ? 'dark' : 'light');
        }
    });
});