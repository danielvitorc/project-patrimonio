from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AdminUserCreationForm(UserCreationForm):
    """Formulário customizado para criação de usuários pelo admin"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    is_admin = forms.BooleanField(required=False, label='É Administrador')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')