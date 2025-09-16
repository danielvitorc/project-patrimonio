from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from patrimonio.forms import AdminUserCreationForm
from patrimonio.models import UserProfile, ActivityLog

def log_activity(user, action):
    ActivityLog.objects.create(user=user, action=action)

# Decorator para verificar se o usuário é admin
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'Acesso negado. Você não tem permissão de administrador.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard(request):
    """Dashboard principal do administrador"""
    total_usuarios = User.objects.count()
    usuarios_bloqueados = UserProfile.objects.filter(is_blocked=True).count()
    usuarios_admin = UserProfile.objects.filter(is_admin=True).count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    
    # Resumo de Atividades
    atividades_recentes = ActivityLog.objects.all().order_by("-timestamp")[:10] # Últimas 10 atividades
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_bloqueados': usuarios_bloqueados,
        'usuarios_admin': usuarios_admin,
        'usuarios_ativos': usuarios_ativos,
        'atividades_recentes': atividades_recentes,
    }
    return render(request, 'patrimonio/admin/dashboard.html', context)

@admin_required
def admin_usuarios(request):
    """Lista todos os usuários para gerenciamento"""
    usuarios = User.objects.all().order_by('username')
    return render(request, 'patrimonio/admin/usuarios.html', {'usuarios': usuarios})


@admin_required
def admin_criar_usuario(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Criar ou atualizar perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_admin = form.cleaned_data.get('is_admin', False)
            profile.save()
            
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            log_activity(request.user, f'Criou o usuário {user.username}')
            return redirect('admin_usuarios')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'patrimonio/admin/criar_usuario.html', {'form': form})

@admin_required
def admin_editar_usuario(request, user_id):
    """Editar usuário existente"""
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Atualizar dados básicos
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name = request.POST.get('last_name', '')
        usuario.email = request.POST.get('email', '')
        usuario.is_active = 'is_active' in request.POST
        usuario.save()
        
        # Atualizar perfil
        profile, created = UserProfile.objects.get_or_create(user=usuario)
        profile.is_admin = 'is_admin' in request.POST
        profile.is_blocked = 'is_blocked' in request.POST
        profile.save()
        
        messages.success(request, f'Usuário {usuario.username} atualizado com sucesso!')
        log_activity(request.user, f'Atualizou o usuário {usuario.username}')
        return redirect('admin_usuarios')
    
    return render(request, 'patrimonio/admin/editar_usuario.html', {'usuario': usuario})

@admin_required
def admin_trocar_senha(request, user_id):
    """Trocar senha de um usuário"""
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if nova_senha and nova_senha == confirmar_senha:
            if len(nova_senha) >= 8:
                usuario.set_password(nova_senha)
                usuario.save()
                messages.success(request, f'Senha do usuário {usuario.username} alterada com sucesso!')
                log_activity(request.user, f'Alterou a senha do usuário {usuario.username}')
                return redirect('admin_usuarios')
            else:
                messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
        else:
            messages.error(request, 'As senhas não coincidem.')
    
    return render(request, 'patrimonio/admin/trocar_senha.html', {'usuario': usuario})

@admin_required
def admin_bloquear_usuario(request, user_id):
    """Bloquear/desbloquear usuário"""
    usuario = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=usuario)
    
    # Não permitir que o admin se bloqueie
    if usuario == request.user:
        messages.error(request, 'Você não pode bloquear sua própria conta.')
        return redirect('admin_usuarios')
    
    profile.is_blocked = not profile.is_blocked
    profile.save()
    
    status = 'bloqueado' if profile.is_blocked else 'desbloqueado'
    messages.success(request, f'Usuário {usuario.username} {status} com sucesso!')
    log_activity(request.user, f'{status.capitalize()} o usuário {usuario.username}')
    return redirect('admin_usuarios')

@admin_required
def admin_excluir_usuario(request, user_id):
    """Excluir usuário"""
    usuario = get_object_or_404(User, id=user_id)
    
    # Não permitir que o admin se exclua
    if usuario == request.user:
        messages.error(request, 'Você não pode excluir sua própria conta.')
        return redirect('admin_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuário {username} excluído com sucesso!')
        log_activity(request.user, f'Excluiu o usuário {username}')
        return redirect('admin_usuarios')
    
    return render(request, 'patrimonio/admin/confirmar_exclusao.html', {'usuario': usuario})