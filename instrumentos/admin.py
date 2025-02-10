from django.contrib import admin
from .models import Categoria, SubCategoria, Marca, Modelo, Instrumento, FotoInstrumento

# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']

@admin.register(SubCategoria)
class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'descricao']
    list_filter = ['categoria']
    search_fields = ['nome']

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pais_origem', 'site']
    search_fields = ['nome']

@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marca', 'subcategoria']
    list_filter = ['marca', 'subcategoria']
    search_fields = ['nome']

class FotoInstrumentoInline(admin.TabularInline):
    model = FotoInstrumento
    extra = 1

@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marca', 'modelo', 'preco', 'status', 'data_aquisicao']
    list_filter = ['status', 'estado', 'marca', 'categoria']
    search_fields = ['nome', 'numero_serie', 'descricao']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FotoInstrumentoInline]
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['nome', 'numero_serie', 'descricao']
        }),
        ('Classificação', {
            'fields': ['categoria', 'subcategoria', 'marca', 'modelo']
        }),
        ('Valores', {
            'fields': ['preco', 'valor_venda']
        }),
        ('Estado e Status', {
            'fields': ['estado', 'status']
        }),
        ('Datas', {
            'fields': ['data_aquisicao', 'data_venda', 'created_at', 'updated_at']
        }),
    ]

@admin.register(FotoInstrumento)
class FotoInstrumentoAdmin(admin.ModelAdmin):
    list_display = ['instrumento', 'descricao', 'ordem']
    list_filter = ['instrumento']
    search_fields = ['descricao']
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['created_at'].initial = timezone.now()
        return form
