# Generated by Django 5.2 on 2025-06-17 17:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patrimonio', '0026_remove_fornecedorservico_data_hora_entrada_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entradafornecedor',
            name='documento',
        ),
        migrations.RemoveField(
            model_name='entradafornecedor',
            name='quantidade',
        ),
        migrations.RemoveField(
            model_name='entradafornecedor',
            name='responsavel',
        ),
        migrations.RemoveField(
            model_name='entradafornecedor',
            name='setor',
        ),
        migrations.RemoveField(
            model_name='entradafornecedor',
            name='tipo_documento',
        ),
        migrations.RemoveField(
            model_name='entradafornecedor',
            name='visitantes',
        ),
        migrations.AddField(
            model_name='entradafornecedor',
            name='usuario_registro',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
