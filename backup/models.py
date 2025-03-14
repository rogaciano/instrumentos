# Create your models here.
from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

class Marca(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    pais_origem = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nome']

class Modelo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome'],
                name='unique_modelo_nome'
            )
        ]

class SubCategoria(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.categoria} - {self.nome}"

    class Meta:
        verbose_name = 'SubCategoria'
        verbose_name_plural = 'SubCategorias'
        ordering = ['categoria', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome', 'categoria'],
                name='unique_subcategoria_nome_categoria'
            )
        ]

class Instrumento(models.Model):
    nome = models.CharField(max_length=200)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    ano_fabricacao = models.IntegerField()
    valor_aquisicao = models.DecimalField(max_digits=10, decimal_places=2)
    valor_mercado = models.DecimalField(max_digits=10, decimal_places=2)
    numero_serie = models.CharField(max_length=100, blank=True)
    caracteristicas = models.TextField()
    data_aquisicao = models.DateField()
    estado_conservacao = models.CharField(
        max_length=20,
        choices=[
            ('novo', 'Novo'),
            ('excelente', 'Excelente'),
            ('bom', 'Bom'),
            ('regular', 'Regular'),
            ('ruim', 'Ruim')
        ]
    )

    def __str__(self):
        return f"{self.nome} - {self.marca} {self.modelo}"

    class Meta:
        verbose_name = 'Instrumento'
        verbose_name_plural = 'Instrumentos'

class FotoInstrumento(models.Model):
    instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='instrumentos/', blank=True, null=True)
    descricao = models.CharField(max_length=100, blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.instrumento}"

    class Meta:
        verbose_name = 'Foto do Instrumento'
        verbose_name_plural = 'Fotos dos Instrumentos'