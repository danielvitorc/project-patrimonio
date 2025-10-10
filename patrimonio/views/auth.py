from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from patrimonio.models import UserProfile

# ===== Tela de Login ===== 
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Verificar se o usuário tem perfil
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
            
            # Verificar se o usuário está bloqueado
            if user.profile.is_blocked:
                messages.error(request, 'Sua conta está bloqueada. Entre em contato com o administrador.')
                return render(request, 'patrimonio/login.html')
            
            login(request, user)
            
            # Redirecionar para tela de admin se for administrador
            if user.profile.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('home')  # Redirecionar para a página inicial pós-login
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'patrimonio/login.html')


# ==== Função para deslogar do sistema =====
def logout_usuario(request):
    logout(request)
    return redirect('login')
