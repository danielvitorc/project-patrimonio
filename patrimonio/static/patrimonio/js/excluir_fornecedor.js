document.addEventListener("DOMContentLoaded", () => {
    const botoesExcluir = document.querySelectorAll(".btn-excluir");

    botoesExcluir.forEach(botao => {
        botao.addEventListener("click", (e) => {
            e.preventDefault();
            const fornecedorId = botao.getAttribute("data-id");

            if (confirm("Tem certeza que deseja excluir este fornecedor?")) {
                fetch(window.excluirFornecedorURL, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": window.csrfToken,
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: new URLSearchParams({ id: fornecedorId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        // Remove a linha da tabela, se existir
                        botao.closest("tr")?.remove();
                    } else {
                        alert("Erro: " + data.message);
                    }
                })
                .catch(error => {
                    console.error("Erro:", error);
                    alert("Erro ao excluir o fornecedor.");
                });
            }
        });
    });
});
