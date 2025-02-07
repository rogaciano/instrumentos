from django import forms
from .models import Categoria, Modelo, Instrumento, Marca, SubCategoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']

class SubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ['nome', 'categoria', 'descricao']

class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['nome', 'marca', 'subcategoria', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InstrumentoForm(forms.ModelForm):
    marca = forms.ModelChoiceField(
        queryset=Marca.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Marca'
    )

    class Meta:
        model = Instrumento
        fields = [
            'codigo', 'modelo', 'numero_serie', 'ano_fabricacao',
            'data_aquisicao', 'preco', 'valor_mercado', 'estado_conservacao',
            'status', 'caracteristicas', 'descricao'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.Select(attrs={'class': 'form-select'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_fabricacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_aquisicao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_mercado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado_conservacao': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'caracteristicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nome', 'pais_origem', 'website']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'pais_origem': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }
