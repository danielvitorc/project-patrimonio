from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_usuario, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_usuario, name='logout'),
    path('livro_de_ocorrencia/', views.livro_de_ocorrencia, name='livro_de_ocorrencia'),
    path('entrega_de_chave/', views.entrega_de_chave, name='entrega_de_chave'),
    path('buscar_colaborador/', views.buscar_colaborador_por_matricula, name='buscar_colaborador'),
    path('devolver_chave/<int:pk>/', views.devolver_chave, name='devolver_chave'),
    path('controle_visitantes/', views.controle_visitantes, name='controle_visitantes'),
    path('status_fornecedor/<int:pk>/', views.status_fornecedor, name='status_fornecedor'),
]