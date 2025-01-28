from django.contrib import admin
from .models import Categoria, Marca, Modelo, Instrumento, FotoInstrumento

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pais_origem')
    search_fields = ('nome',)

@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca')
    search_fields = ('nome', 'marca__nome')
    list_filter = ('marca',)

class FotoInstrumentoInline(admin.TabularInline):
    model = FotoInstrumento
    extra = 1

@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'marca', 'modelo', 'ano_fabricacao', 'preco')
    list_filter = ('categoria', 'marca', 'estado_conservacao')
    search_fields = ('nome', 'numero_serie')
    inlines = [FotoInstrumentoInline]

@admin.register(FotoInstrumento)
class FotoInstrumentoAdmin(admin.ModelAdmin):
    list_display = ('instrumento', 'descricao', 'data_upload')
    list_filter = ('data_upload',)