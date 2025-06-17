from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_usuario, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_usuario, name='logout'),
    path('livro_de_ocorrencia/', views.livro_de_ocorrencia, name='livro_de_ocorrencia'),
    path('ocorrencia_cracha/', views.ocorrencia_cracha, name='ocorrencia_cracha'),
    path('exportar_excel/', views.exportar_ocorrencias_excel, name='exportar_ocorrencias_excel'),
    path('excluir_chave/<int:chave_id>/', views.excluir_chave, name='excluir_chave'),
    path('devolver_chave/<int:pk>/', views.devolver_chave, name='devolver_chave'),
    path('entrega_de_chave/', views.entrega_de_chave, name='entrega_de_chave'),
    path('buscar_colaborador/', views.buscar_colaborador_por_matricula, name='buscar_colaborador'),
    path('devolver_chave/<int:pk>/', views.devolver_chave, name='devolver_chave'),
    path('chave/excluir/<int:id>/', views.excluir_chave, name='excluir_chave'),
    path('controle_visitantes/', views.controle_visitantes, name='controle_visitantes'),
    path('fornecedores-cadastrados/', views.fornecedores_cadastrados_view, name='fornecedores_cadastrados'),
    path('status_fornecedor/<int:pk>/', views.status_fornecedor, name='status_fornecedor'),
    path('entrada/<int:pk>/excluir/', views.excluir_entrada, name='excluir_entrada'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)