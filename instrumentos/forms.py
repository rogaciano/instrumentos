from django import forms
from django.forms import inlineformset_factory
from .models import Categoria, Modelo, Instrumento, Marca, SubCategoria, FotoInstrumento

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class SubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ['nome', 'categoria', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nome', 'descricao', 'pais_origem', 'logotipo', 'site']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['nome', 'marca', 'subcategoria', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class InstrumentoCreateForm(forms.ModelForm):
    class Meta:
        model = Instrumento
        fields = [
            'codigo', 'modelo', 'numero_serie', 'ano_fabricacao',
            'data_aquisicao', 'preco', 'valor_mercado', 'estado_conservacao',
            'status'
        ]
        widgets = {
            'ano_fabricacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_aquisicao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'modelo': forms.Select(attrs={'class': 'form-select select2'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_mercado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado_conservacao': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza o queryset do campo modelo para incluir informações da marca
        self.fields['modelo'].queryset = Modelo.objects.select_related('marca', 'subcategoria')
        self.fields['modelo'].label_from_instance = lambda obj: f"{obj.marca.nome} - {obj.nome} ({obj.subcategoria.nome})"

# Formset para as fotos do instrumento
FotoInstrumentoFormSet = inlineformset_factory(
    Instrumento,
    FotoInstrumento,
    fields=['imagem', 'descricao'],
    extra=3,
    can_delete=True,
    widgets={
        'imagem': forms.FileInput(attrs={'class': 'form-control'}),
        'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição da foto'})
    }
)
