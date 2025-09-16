from django.urls import path
from .views import adm

urlpatterns = [
    path("dashboard/", adm.admin_dashboard, name="admin_dashboard"),
    path("usuarios/", adm.admin_usuarios, name="admin_usuarios"),
    path("usuarios/criar/", adm.admin_criar_usuario, name="admin_criar_usuario"),
    path("usuarios/<int:user_id>/editar/", adm.admin_editar_usuario, name="admin_editar_usuario"),
    path("usuarios/<int:user_id>/trocar-senha/", adm.admin_trocar_senha, name="admin_trocar_senha"),
    path("usuarios/<int:user_id>/bloquear/", adm.admin_bloquear_usuario, name="admin_bloquear_usuario"),
    path("usuarios/<int:user_id>/excluir/", adm.admin_excluir_usuario, name="admin_excluir_usuario"),
]

