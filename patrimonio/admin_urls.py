from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("usuarios/", views.admin_usuarios, name="admin_usuarios"),
    path("usuarios/criar/", views.admin_criar_usuario, name="admin_criar_usuario"),
    path("usuarios/<int:user_id>/editar/", views.admin_editar_usuario, name="admin_editar_usuario"),
    path("usuarios/<int:user_id>/trocar-senha/", views.admin_trocar_senha, name="admin_trocar_senha"),
    path("usuarios/<int:user_id>/bloquear/", views.admin_bloquear_usuario, name="admin_bloquear_usuario"),
    path("usuarios/<int:user_id>/excluir/", views.admin_excluir_usuario, name="admin_excluir_usuario"),
]

