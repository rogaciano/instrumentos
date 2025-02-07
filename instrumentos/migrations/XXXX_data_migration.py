from django.db import migrations

def criar_classe_geral(apps, schema_editor):
    Classe = apps.get_model('instrumentos', 'Classe')
    Categoria = apps.get_model('instrumentos', 'Categoria')
    
    # Criar classe Geral
    classe_geral = Classe.objects.create(
        nome='Geral',
        descricao='Classe padrão para todas as categorias'
    )
    
    # Atualizar todas as categorias existentes
    Categoria.objects.all().update(classe=classe_geral)

def reverter_classe_geral(apps, schema_editor):
    Classe = apps.get_model('instrumentos', 'Classe')
    Categoria = apps.get_model('instrumentos', 'Categoria')
    
    # Limpar referências
    Categoria.objects.all().update(classe=None)
    # Deletar classe Geral
    Classe.objects.filter(nome='Geral').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('instrumentos', 'XXXX_previous_migration'),  # Substitua pelo número da migração anterior
    ]

    operations = [
        migrations.RunPython(criar_classe_geral, reverter_classe_geral),
    ] 