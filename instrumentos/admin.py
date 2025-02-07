from django.contrib import admin
from .models import Categoria, SubCategoria, Marca, Modelo, Instrumento, FotoInstrumento

# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(SubCategoria)
class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'descricao')
    list_filter = ('categoria',)
    search_fields = ('nome', 'categoria__nome')

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pais_origem', 'website')
    search_fields = ('nome', 'pais_origem')

@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'descricao')
    list_filter = ('marca',)
    search_fields = ('nome', 'marca__nome')

@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'modelo', 'preco', 'status')
    list_filter = ('status', 'estado_conservacao')
    search_fields = ('codigo', 'modelo__nome', 'modelo__marca__nome')
    readonly_fields = ('data_cadastro', 'ultima_atualizacao')
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['codigo', 'modelo', 'numero_serie', 'ano_fabricacao']
        }),
        ('Valores', {
            'fields': ['preco', 'valor_mercado']
        }),
        ('Estado e Status', {
            'fields': ['estado_conservacao', 'status']
        }),
        ('Datas', {
            'fields': ['data_aquisicao', 'data_cadastro', 'ultima_atualizacao']
        }),
        ('Descrições', {
            'fields': ['caracteristicas', 'descricao']
        }),
    ]

@admin.register(FotoInstrumento)
class FotoInstrumentoAdmin(admin.ModelAdmin):
    list_display = ('instrumento', 'descricao', 'data_upload')
    list_filter = ('instrumento__modelo__marca', 'data_upload')
    search_fields = ('instrumento__codigo', 'descricao')
