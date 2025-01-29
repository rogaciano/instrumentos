from django import forms
from .models import Instrumento, Categoria, Modelo, FotoInstrumento, Marca

class InstrumentoForm(forms.ModelForm):
    class Meta:
        model = Instrumento
        fields = ['nome', 'categoria', 'marca', 'modelo', 'ano_fabricacao', 
                 'valor_aquisicao', 'valor_mercado', 'numero_serie', 'caracteristicas', 
                 'data_aquisicao', 'estado_conservacao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.Select(attrs={'class': 'form-select'}),
            'ano_fabricacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_aquisicao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_mercado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'caracteristicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data_aquisicao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'estado_conservacao': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_data_aquisicao(self):
        data = self.cleaned_data.get('data_aquisicao')
        if not data:
            raise forms.ValidationError('A data de aquisição é obrigatória.')
        return data

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FotoInstrumentoForm(forms.ModelForm):
    class Meta:
        model = FotoInstrumento
        fields = ['imagem', 'descricao']
        widgets = {
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
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