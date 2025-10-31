// project-patrimonio/patrimonio/static/patrimonio/js/entrega_de_chave.js

document.addEventListener("DOMContentLoaded", function () {

    /**
     * Função reutilizável para buscar dados do colaborador.
     * @param {string} matricula - A matrícula a ser buscada.
     * @returns {Promise<object>} - Uma promessa que resolve com os dados do colaborador.
     */
    function fetchColaborador(matricula) {
        return fetch(`/buscar_colaborador/?matricula=${encodeURIComponent(matricula)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Matrícula não encontrada ou erro no servidor.');
                }
                return response.json();
            })
            .then(data => {
                if (data.erro) {
                    throw new Error(data.erro);
                }
                return data;
            });
    }

    /**
     * Função para configurar o autopreenchimento em um formulário (container).
     * @param {Element} formContainer - O elemento que contém o formulário (ex: o modal).
     * @param {string} matriculaSelector - O seletor (name ou id) do campo de matrícula.
     * @param {string} colaboradorSelector - O seletor (name ou id) do campo de colaborador.
     * @param {string} [departamentoSelector] - Opcional: O seletor (name ou id) do campo de departamento.
     */
    function setupAutofill(formContainer, matriculaSelector, colaboradorSelector, departamentoSelector) {
        const matriculaInput = formContainer.querySelector(matriculaSelector);
        const colaboradorInput = formContainer.querySelector(colaboradorSelector);
        const departamentoInput = departamentoSelector ? formContainer.querySelector(departamentoSelector) : null;

        if (!matriculaInput || !colaboradorInput) {
            console.warn("Campos de matrícula ou colaborador não encontrados para autofill.");
            return;
        }

        const clearFields = () => {
            colaboradorInput.value = "";
            if (departamentoInput) departamentoInput.value = "";
        };

        matriculaInput.addEventListener("blur", function () {
            const matricula = this.value.trim();
            if (!matricula) {
                clearFields();
                return;
            }

            fetchColaborador(matricula)
                .then(data => {
                    colaboradorInput.value = data.nome || "";
                    if (departamentoInput) departamentoInput.value = data.departamento || "";
                })
                .catch(error => {
                    alert(error.message);
                    clearFields();
                });
        });

        matriculaInput.addEventListener("input", function () {
            if (this.value.trim() === "") {
                clearFields();
            }
        });
    }

    // --- LÓGICA PARA O MODAL DE CADASTRO (ENTREGA) ---
    const modalCadastro = document.getElementById('modalCadastroChaveOverlay');
    if (modalCadastro) {
        // Configura autopreenchimento para "Recebendo"
        setupAutofill(
            modalCadastro,
            "[name='matricula_recebendo']",
            "[name='colaborador_recebendo']",
            "[name='departamento']"
        );
    }

    // --- LÓGICA PARA OS MODAIS DE DEVOLUÇÃO (Dentro do Loop) ---
    const devolucoesModals = document.querySelectorAll('[id^="modalDevolverOverlay"]');
    devolucoesModals.forEach(modal => {
        // Configura autopreenchimento para "Devolveu"
        setupAutofill(
            modal,
            "[name='matricula_devolveu']",
            "[name='colaborador_devolveu']"
            // Sem departamento na devolução
        );
    });

    // --- LÓGICA PARA OS FILTROS DA TABELA ---
    const filterDepartamento = document.getElementById('filterDepartamento');
    const filterMatricula = document.getElementById('filterMatricula');
    const filterSituacao = document.getElementById('filterSituacao');
    const filterData = document.getElementById('filterData');
    const tableRows = document.querySelectorAll('table.data-table tbody tr[data-situacao]'); // Seleciona apenas linhas de dados

    function normalize(text) {
        return text ? text.trim().toLowerCase() : "";
    }

    function filterRows() {
        const depValue = normalize(filterDepartamento ? filterDepartamento.value : "");
        const matValue = normalize(filterMatricula ? filterMatricula.value : "");
        const situacaoValue = normalize(filterSituacao ? filterSituacao.value : "");
        const dataValue = filterData ? filterData.value : ""; // formato yyyy-mm-dd

        tableRows.forEach(row => {
            const rowDep = normalize(row.getAttribute('data-departamento'));
            const rowMat = normalize(row.getAttribute('data-matricula'));
            const rowSituacao = normalize(row.getAttribute('data-situacao'));
            const rowData = row.getAttribute('data-data-saida') || '';

            const showDep = !depValue || rowDep.includes(depValue);
            const showMat = !matValue || rowMat.includes(matValue);
            const showSituacao = !situacaoValue || rowSituacao === situacaoValue;
            const showData = !dataValue || rowData === dataValue;

            row.style.display = (showDep && showMat && showSituacao && showData) ? '' : 'none';
        });
    }

    // Adiciona eventos aos filtros
    [filterDepartamento, filterMatricula, filterSituacao, filterData].forEach(input => {
        if (input) {
            input.addEventListener('input', filterRows); // 'change' para select/date, 'input' para text
            input.addEventListener('change', filterRows);
        }
    });

    // Nota: A lógica de Toasts será substituída por um componente de Mensagens.
    // A lógica da sidebar já está no sidebar.js.
});