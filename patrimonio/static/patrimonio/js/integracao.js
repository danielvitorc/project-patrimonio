// -------------------- Função CSRF --------------------
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

// -------------------- Botão gerar link --------------------
document.addEventListener('DOMContentLoaded', function() {
    console.log("🟢 Script fornecedores.js carregado.");

    // Botão gerar link (fetch)
    document.querySelectorAll('.btn-gerar-link').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const fornecedorId = this.dataset.id;
            const validade = prompt("Informe a validade em meses:");

            if (!validade) {
                alert("Você precisa informar a validade em meses.");
                return;
            }

            fetch(`/gerar-link-integracao/${fornecedorId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: new URLSearchParams({ validade_meses: validade })
            })
            .then(response => response.json())
            .then(data => {
                if (data.erro) {
                    alert(data.erro);
                    return;
                }
                const modal = `
                    <div class="modal fade" id="modalLink${fornecedorId}" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog modal-dialog-centered">
                            <div class="modal-content p-3">
                                <h5 class="mb-2">🔗 Link de Integração</h5>
                                <input class="form-control mb-2" value="${data.link}" readonly>
                                <h6 class="mt-3">🔑 Token de Acesso</h6>
                                <input class="form-control mb-3" value="${data.token}" readonly>
                                <small class="text-muted">${data.mensagem}</small>
                            </div>
                        </div>
                    </div>`;
                document.body.insertAdjacentHTML("beforeend", modal);
                new bootstrap.Modal(document.getElementById(`modalLink${fornecedorId}`)).show();
            });
        });
    });

    // -------------------- Botão confirmar link (jQuery) --------------------
    if (window.jQuery) {
        $('body').on('click', '.btn-confirmar-link', function(e) {
            e.preventDefault();
            console.log("🚀 Clique detectado dentro do modal!");

            const fornecedorId = $(this).data('id');
            const validade = $('#validadeMeses' + fornecedorId).val();

            if (!validade) {
                alert("Informe a validade em meses!");
                return;
            }

            $.ajax({
                url: window.gerarLinkUrl.replace("0", fornecedorId),
                method: "POST",
                data: {
                    validade_meses: validade,
                    csrfmiddlewaretoken: window.csrfToken
                },
                success: function(response) {
                    // Fecha o modal de validade
                    const modalEl = document.getElementById('modalValidade' + fornecedorId);
                    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                    modal.hide();

                    // Preenche o modal genérico com token e link
                    $('#tokenGerado').text(response.token);
                    $('#linkGerado').text(response.link).attr('href', response.link);

                    // Abre o modal genérico
                    const modalLinkEl = document.getElementById('modalLinkGerado');
                    const modalLink = new bootstrap.Modal(modalLinkEl);
                    modalLink.show();
                },
                error: function(xhr) {
                    alert("Erro: " + (xhr.responseJSON?.erro || xhr.statusText));
                }
            });
        });
    }
});
