from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Modelo para perfil de usuário com controle de admin e bloqueio
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(default=False, verbose_name='É Administrador')
    is_blocked = models.BooleanField(default=False, verbose_name='Usuário Bloqueado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - Admin: {self.is_admin} - Bloqueado: {self.is_blocked}'

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)

# Modelo para registrar atividades do sistema
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    action = models.CharField(max_length=255, verbose_name="Ação")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Registro de Atividade"
        verbose_name_plural = "Registros de Atividades"

    def __str__(self):
        return f"{self.user.username} - {self.action} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"