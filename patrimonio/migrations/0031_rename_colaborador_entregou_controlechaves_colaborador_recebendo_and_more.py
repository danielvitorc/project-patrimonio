# Generated by Django 5.2 on 2025-07-14 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patrimonio', '0030_remove_entrega_imagem_material'),
    ]

    operations = [
        migrations.RenameField(
            model_name='controlechaves',
            old_name='colaborador_entregou',
            new_name='colaborador_recebendo',
        ),
        migrations.RenameField(
            model_name='controlechaves',
            old_name='matricula_entregou',
            new_name='matricula_recebendo',
        ),
    ]
