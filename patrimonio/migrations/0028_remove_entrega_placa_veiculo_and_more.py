# Generated by Django 5.2 on 2025-07-11 15:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patrimonio', '0027_remove_entradafornecedor_documento_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entrega',
            name='placa_veiculo',
        ),
        migrations.RemoveField(
            model_name='entrega',
            name='quantidade_recebida',
        ),
        migrations.RemoveField(
            model_name='entrega',
            name='setor_destino',
        ),
        migrations.RemoveField(
            model_name='fornecedorservico',
            name='modelo_veiculo',
        ),
        migrations.RemoveField(
            model_name='fornecedorservico',
            name='placa_veiculo',
        ),
        migrations.RemoveField(
            model_name='fornecedorservico',
            name='responsavel_autorizante',
        ),
        migrations.RemoveField(
            model_name='fornecedorservico',
            name='setor_destino',
        ),
        migrations.RemoveField(
            model_name='visitante',
            name='modelo_veiculo',
        ),
        migrations.RemoveField(
            model_name='visitante',
            name='placa_veiculo',
        ),
        migrations.RemoveField(
            model_name='visitante',
            name='responsavel_autorizante',
        ),
        migrations.RemoveField(
            model_name='visitante',
            name='setor_destino',
        ),
        migrations.AddField(
            model_name='entradafornecedor',
            name='modelo_veiculo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='entradafornecedor',
            name='placa_veiculo',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='entradafornecedor',
            name='responsavel_autorizante',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='entradafornecedor',
            name='setor_destino',
            field=models.CharField(default='Almoxarifado', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entrega',
            name='foto_caixa_entrega',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_entregas/'),
        ),
        migrations.AddField(
            model_name='fornecedorservico',
            name='foto_fornecedor',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_fornecedores/'),
        ),
        migrations.AddField(
            model_name='visitante',
            name='foto_visitante',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_visitantes/'),
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255, verbose_name='Ação')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Registro de Atividade',
                'verbose_name_plural': 'Registros de Atividades',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False, verbose_name='É Administrador')),
                ('is_blocked', models.BooleanField(default=False, verbose_name='Usuário Bloqueado')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Usuário',
                'verbose_name_plural': 'Perfis de Usuários',
            },
        ),
    ]
