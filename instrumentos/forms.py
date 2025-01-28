from django import forms
from .models import Instrumento, Categoria, Modelo

class InstrumentoForm(forms.ModelForm):
    class Meta:
        model = Instrumento
        fields = ['nome', 'categoria', 'modelo', 'ano_fabricacao', 
                 'preco', 'numero_serie', 'caracteristicas', 
                 'data_aquisicao', 'estado_conservacao']

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']

class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['nome', 'descricao'] 