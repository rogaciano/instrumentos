from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('instrumentos', '0001_initial'),  # Ajuste para sua última migração
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelo',
            name='marca',
        ),
    ] 