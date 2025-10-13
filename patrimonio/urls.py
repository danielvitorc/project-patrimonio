from django.urls import path
from .views import auth, adm, home, controle_visitantes, chave, cracha, ocorrencias, export_excel 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Urls de Auth
    path('login/', auth.login_usuario, name='login'),
    path('logout/', auth.logout_usuario, name='logout'),

    # Urls de Home
    path('home/', home.home, name='home'),

    # Urls de Controle de Visitantes
    path('controle_visitantes/', controle_visitantes.controle_visitantes, name='controle_visitantes'),
    path('fornecedor/excluir/<int:pk>/', controle_visitantes.excluir_fornecedor, name='excluir_fornecedor'),
    path('status_fornecedor/<int:pk>/', controle_visitantes.status_fornecedor, name='status_fornecedor'),
    path('fornecedores-cadastrados/', controle_visitantes.fornecedores_cadastrados, name='fornecedores-cadastrados'),
    path("fornecedor/<int:pk>/editar/", controle_visitantes.modal_editar_fornecedor_completo, name="modal_editar_fornecedor_completo"),
    path("fornecedor/<int:pk>/dados/", controle_visitantes.carregar_dados_fornecedor, name="carregar_dados_fornecedor"),
    path('entrada/<int:pk>/excluir/', controle_visitantes.excluir_entrada, name='excluir_entrada'),
    path('gerar-link-integracao/<int:fornecedor_id>/', controle_visitantes.gerar_link_integracao, name='gerar_link_integracao'),
    path('integracao/sucesso/', controle_visitantes.integracao_sucesso, name='integracao_sucesso'),
    path('integracao/<uuid_link>/', controle_visitantes.pagina_integracao_externa, name='pagina_integracao_externa'),



    path("fornecedores/", controle_visitantes.fornecedores_cadastrados, name="fornecedores_cadastrados"),

    # Urls de Chaves
    path('entrega_de_chave/', chave.entrega_de_chave, name='entrega_de_chave'),
    path('chave/excluir/<int:id>/', chave.excluir_chave, name='excluir_chave'),
    path('devolver_chave/<int:pk>/', chave.devolver_chave, name='devolver_chave'),
    path('buscar_colaborador/', chave.buscar_colaborador_por_matricula, name='buscar_colaborador'),

    # Urls de Crachá
    path('ocorrencia_cracha/', cracha.ocorrencia_cracha, name='ocorrencia_cracha'),
    path('exportar_excel/', cracha.exportar_ocorrencias_excel, name='exportar_ocorrencias_excel'),

    # Urls de Ocorrências
    path('livro_de_ocorrencia/', ocorrencias.livro_de_ocorrencia, name='livro_de_ocorrencia'),
    
    # Urls de Exportação excel
    path('exportar-fornecedores-excel/', export_excel.exportar_fornecedores_excel, name='exportar_fornecedores_excel'),
    path('exportar-fornecedores-servico-excel/', export_excel.exportar_fornecedores_servico_excel, name='exportar_fornecedores_servico_excel'),
    path('exportar-visitantes-excel/', export_excel.exportar_visitantes_excel, name='exportar_visitantes_excel'),
    
    # URLs de Administração
    path("dashboard/", adm.admin_dashboard, name="admin_dashboard"),
    path("usuarios/", adm.admin_usuarios, name="admin_usuarios"),
    path("usuarios/criar/", adm.admin_criar_usuario, name="admin_criar_usuario"),
    path("usuarios/<int:user_id>/editar/", adm.admin_editar_usuario, name="admin_editar_usuario"),
    path("usuarios/<int:user_id>/trocar-senha/", adm.admin_trocar_senha, name="admin_trocar_senha"),
    path("usuarios/<int:user_id>/bloquear/", adm.admin_bloquear_usuario, name="admin_bloquear_usuario"),
    path("usuarios/<int:user_id>/excluir/", adm.admin_excluir_usuario, name="admin_excluir_usuario"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)