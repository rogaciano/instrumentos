# Generated by Django 5.1.5 on 2025-01-28 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instrumentos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fotoinstrumento',
            name='descricao',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='fotoinstrumento',
            name='imagem',
            field=models.ImageField(blank=True, null=True, upload_to='instrumentos/'),
        ),
        migrations.AlterField(
            model_name='fotoinstrumento',
            name='instrumento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instrumentos.instrumento'),
        ),
    ]
