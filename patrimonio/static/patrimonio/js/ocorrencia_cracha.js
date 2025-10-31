// project-patrimonio/patrimonio/static/patrimonio/js/ocorrencia_cracha.js

document.addEventListener("DOMContentLoaded", function() {

    // --- Lógica de Filtro da Tabela ---
    const filtroColaborador = document.getElementById("filtroColaborador");
    const filtroData = document.getElementById("filtroData");
    const tabelaRegistrosBody = document.getElementById("tabelaRegistros"); // Seleciona o tbody
    const linhasTabela = tabelaRegistrosBody ? tabelaRegistrosBody.querySelectorAll("tr") : []; // Pega as linhas dentro do tbody

    function aplicarFiltro() {
        if (!tabelaRegistrosBody) return; // Sai se a tabela não for encontrada

        const termoColaborador = filtroColaborador ? filtroColaborador.value.toLowerCase() : "";
        const dataSelecionada = filtroData ? filtroData.value : ""; // yyyy-mm-dd

        // Converte de yyyy-mm-dd para dd/mm/yyyy para comparação com o texto da célula
        let termoData = "";
        if (dataSelecionada) {
            const partes = dataSelecionada.split("-");
            if (partes.length === 3) {
                termoData = `${partes[2]}/${partes[1]}/${partes[0]}`;
            }
        }

        linhasTabela.forEach(linha => {
            // Verifica se a linha tem as células esperadas
            if (linha.children.length < 4) return;

            const colaborador = linha.children[1].textContent.toLowerCase();
            const dataTexto = linha.children[3].textContent.trim(); // dd/mm/yyyy

            const correspondeColaborador = !termoColaborador || colaborador.includes(termoColaborador);
            const correspondeData = !termoData || dataTexto === termoData;

            if (correspondeColaborador && correspondeData) {
                linha.style.display = ""; // Mostra a linha
            } else {
                linha.style.display = "none"; // Esconde a linha
            }
        });
    }

    // Adiciona eventos aos filtros, se existirem
    if (filtroColaborador) {
        filtroColaborador.addEventListener("input", aplicarFiltro);
    }
    if (filtroData) {
        filtroData.addEventListener("input", aplicarFiltro);
    }

    // --- Lógica de Autopreenchimento do Modal ---
    const modalOcorrencia = document.getElementById('modalOcorrenciaOverlay');

    if (modalOcorrencia) {
        // Seleciona os campos DENTRO do modal
        const matriculaInput = modalOcorrencia.querySelector("#id_matricula"); // Use o ID gerado pelo Django
        const colaboradorInput = modalOcorrencia.querySelector("#id_colaborador");
        const departamentoInput = modalOcorrencia.querySelector("#id_departamento");
        const form = modalOcorrencia.querySelector("form");

        if (matriculaInput && colaboradorInput && departamentoInput && form) {

            // Função para limpar os campos colaborador e departamento
            function limparCamposCracha() {
                if (colaboradorInput) colaboradorInput.value = "";
                if (departamentoInput) departamentoInput.value = "";
            }

            // Ao sair do campo matrícula, faz a busca
            matriculaInput.addEventListener("blur", function() {
                const matricula = this.value.trim();

                if (matricula === "") {
                    limparCamposCracha();
                    return;
                }

                // Assume que a URL /buscar_colaborador/ está correta
                fetch(`/buscar_colaborador/?matricula=${encodeURIComponent(matricula)}`)
                    .then(response => {
                        if (!response.ok) {
                            // Se a resposta não for OK (ex: 404), trata como erro
                             limparCamposCracha();
                             // Lança um erro para ser pego pelo catch
                             throw new Error(`Erro ${response.status}: Matrícula não encontrada ou erro no servidor.`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Verifica se a resposta JSON contém um erro explícito
                        if (data.erro) {
                            alert(data.erro); // Mostra o erro retornado pela view
                            limparCamposCracha();
                        } else if (data.nome && data.departamento) {
                            // Preenche os campos se os dados existirem
                            colaboradorInput.value = data.nome;
                            departamentoInput.value = data.departamento;
                        } else {
                            // Caso a resposta não tenha erro mas falte dados
                            alert("Dados do colaborador não encontrados para esta matrícula.");
                            limparCamposCracha();
                        }
                    })
                    .catch(error => {
                        // Captura erros de rede ou o erro lançado pelo !response.ok
                        console.error("Erro ao buscar colaborador:", error);
                        // Informa o usuário de forma genérica ou usa error.message
                        alert(error.message || "Ocorreu um erro ao buscar os dados.");
                        limparCamposCracha();
                    });
            });

            // Se o campo matrícula for apagado manualmente, limpar os outros campos
            matriculaInput.addEventListener("input", function() {
                if (this.value.trim() === "") {
                    limparCamposCracha();
                }
            });

            // Validação antes do envio do formulário (opcional, mas recomendado)
            form.addEventListener("submit", function(event) {
                const matricula = matriculaInput.value.trim();
                const colaborador = colaboradorInput.value.trim();
                const departamento = departamentoInput.value.trim();

                if (matricula !== "" && (colaborador === "" || departamento === "")) {
                    // Impede o envio apenas se a matrícula foi digitada mas os dados não foram preenchidos
                    event.preventDefault();
                    alert("Matrícula inválida ou dados do colaborador incompletos. Por favor, verifique a matrícula e tente novamente.");
                    matriculaInput.focus(); // Coloca o foco de volta na matrícula
                }
            });
        } else {
             console.warn("Campos de matrícula, colaborador ou departamento não encontrados no modal #modalOcorrencia.");
        }
    } else {
         console.warn("Modal com ID #modalOcorrencia não encontrado.");
    }

    // Nota: A lógica da sidebar já foi movida para sidebar.js e incluída no base.html,
    // então não precisamos mais dela aqui.

}); // Fim do DOMContentLoaded