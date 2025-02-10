from django import forms
from django.forms import inlineformset_factory
from .models import Categoria, Modelo, Instrumento, Marca, SubCategoria, FotoInstrumento

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class SubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ['nome', 'categoria', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nome', 'descricao', 'pais_origem', 'logotipo', 'site']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['nome', 'marca', 'subcategoria', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class InstrumentoCreateForm(forms.ModelForm):
    class Meta:
        model = Instrumento
        fields = ['nome', 'numero_serie', 'categoria', 'subcategoria', 'marca', 'modelo', 
                 'preco', 'data_aquisicao', 'estado', 'status', 'valor_venda', 'data_venda', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.Select(attrs={'class': 'form-select'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_aquisicao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'valor_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_venda': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategoria'].queryset = SubCategoria.objects.none()
        self.fields['modelo'].queryset = Modelo.objects.none()

        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = SubCategoria.objects.filter(categoria_id=categoria_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.categoria:
            self.fields['subcategoria'].queryset = self.instance.categoria.subcategoria_set.all()

        if 'marca' in self.data:
            try:
                marca_id = int(self.data.get('marca'))
                self.fields['modelo'].queryset = Modelo.objects.filter(marca_id=marca_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.marca:
            self.fields['modelo'].queryset = self.instance.marca.modelo_set.all()

        # Tornar campos não obrigatórios
        self.fields['valor_venda'].required = False
        self.fields['data_venda'].required = False
        self.fields['descricao'].required = False

class FotoInstrumentoForm(forms.ModelForm):
    class Meta:
        model = FotoInstrumento
        fields = ['imagem', 'descricao']
        widgets = {
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Formset para as fotos do instrumento
FotoInstrumentoFormSet = inlineformset_factory(
    Instrumento,
    FotoInstrumento,
    form=FotoInstrumentoForm,
    extra=3,
    can_delete=True
)
