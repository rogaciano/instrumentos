from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

class SubCategoria(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.categoria.nome} - {self.nome}"

    class Meta:
        verbose_name = 'Subcategoria'
        verbose_name_plural = 'Subcategorias'
        ordering = ['categoria__nome', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome', 'categoria'],
                name='unique_subcategoria_nome_categoria'
            )
        ]

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
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos', default=1)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, related_name='modelos')
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.marca.nome} - {self.nome}"

    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        ordering = ['marca__nome', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome', 'marca'],
                name='unique_modelo_nome_marca'
            )
        ]

class Instrumento(models.Model):
    ESTADO_CHOICES = [
        ('novo', 'Novo'),
        ('excelente', 'Excelente'),
        ('muito_bom', 'Muito Bom'),
        ('bom', 'Bom'),
        ('regular', 'Regular'),
        ('ruim', 'Ruim')
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('vendido', 'Vendido'),
        ('reservado', 'Reservado'),
        ('manutencao', 'Em Manutenção'),
    ]

    codigo = models.CharField('Código', max_length=50, unique=True, default='INST001')
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    numero_serie = models.CharField('Número de Série', max_length=100, blank=True)
    ano_fabricacao = models.IntegerField('Ano de Fabricação', null=True, blank=True)
    data_aquisicao = models.DateField('Data de Aquisição', default=timezone.now)
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    valor_mercado = models.DecimalField('Valor de Mercado', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    estado_conservacao = models.CharField('Estado de Conservação', max_length=20, choices=ESTADO_CHOICES, default='bom')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='disponivel')
    caracteristicas = models.TextField('Características', blank=True)
    descricao = models.TextField('Descrição', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True, null=True)
    ultima_atualizacao = models.DateTimeField('Última Atualização', auto_now=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.modelo}"

    class Meta:
        verbose_name = 'Instrumento'
        verbose_name_plural = 'Instrumentos'
        ordering = ['-id']

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
        ordering = ['-data_upload']