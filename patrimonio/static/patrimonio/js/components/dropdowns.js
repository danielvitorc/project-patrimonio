// project-patrimonio/patrimonio/static/patrimonio/js/components/dropdowns.js

document.addEventListener('click', function(e) {
    // Procura por um clique em um botão de dropdown
    const toggleButton = e.target.closest('[data-dropdown-button]');

    if (toggleButton) {
        // Encontra o container pai
        const dropdown = toggleButton.closest('[data-dropdown]');
        // Alterna a classe 'active'
        dropdown.classList.toggle('active');
    } else {
        // Se o clique NÃO foi em um botão, fecha todos os dropdowns abertos
        // Verifica se o clique foi DENTRO de um menu (para não fechar ao clicar no menu)
        if (!e.target.closest('.dropdown-menu')) {
            document.querySelectorAll('[data-dropdown].active').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    }
});