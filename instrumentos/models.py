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
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    pais_origem = models.CharField(max_length=100, blank=True, null=True)
    logotipo = models.ImageField(
        upload_to='logos/', 
        blank=True, 
        null=True,
        help_text='Upload de logotipo da marca. Recomendado: PNG com fundo transparente, mínimo 300x300 pixels.'

    )
    site = models.URLField(blank=True, null=True, help_text='Site oficial da marca')
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
    
    def __str__(self):
        return self.nome

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
        ('usado', 'Usado'),
        ('restaurado', 'Restaurado'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('vendido', 'Vendido'),
        ('reservado', 'Reservado'),
        ('manutencao', 'Em Manutenção'),
    ]

    nome = models.CharField(max_length=200, null=True, blank=True)  
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.PROTECT, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, null=True)
    modelo = models.ForeignKey(Modelo, on_delete=models.PROTECT, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True)  
    data_aquisicao = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='novo')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    valor_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_venda = models.DateField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.numero_serie}" if self.marca and self.modelo else "Instrumento sem identificação"

    class Meta:
        verbose_name = 'Instrumento'
        verbose_name_plural = 'Instrumentos'
        ordering = ['-created_at']

class FotoInstrumento(models.Model):
    instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='instrumentos/', null=True, blank=True)
    descricao = models.CharField(max_length=200, blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Foto {self.ordem} - {self.instrumento}"

    class Meta:
        verbose_name = 'Foto do Instrumento'
        verbose_name_plural = 'Fotos do Instrumento'
        ordering = ['ordem']