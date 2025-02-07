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

class MultipleFileField(forms.Field):
    def __init__(self, *args, **kwargs):
        self.allow_empty_file = kwargs.pop('allow_empty_file', False)
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['multiple'] = True
        attrs['accept'] = 'image/*'
        return attrs

    def to_python(self, data):
        if data in self.empty_values:
            return []
        return data.getlist('fotos')

    def validate(self, value):
        super().validate(value)
        for file in value:
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(f'A foto {file.name} é muito grande. O tamanho máximo é 5MB.')
            
            import imghdr
            if not imghdr.what(file):
                raise forms.ValidationError(f'O arquivo {file.name} não é uma imagem válida.')

class InstrumentoCreateForm(InstrumentoForm):
    class Meta(InstrumentoForm.Meta):
        fields = InstrumentoForm.Meta.fields

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nome', 'descricao', 'logotipo', 'site']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
    
    def clean_logotipo(self):
        logotipo = self.cleaned_data.get('logotipo')
        if logotipo:
            # Verifica o tamanho do arquivo (max 2MB)
            if logotipo.size > 2 * 1024 * 1024:
                raise forms.ValidationError('O arquivo é muito grande. O tamanho máximo é 2MB.')
            
            # Verifica as dimensões
            try:
                from PIL import Image
                img = Image.open(logotipo)
                width, height = img.size
                
                if width < 300 or height < 300:
                    raise forms.ValidationError(
                        f'A imagem é muito pequena ({width}x{height}px). '
                        'O tamanho mínimo é 300x300 pixels.'
                    )
            except Exception as e:
                raise forms.ValidationError(f'Erro ao processar imagem: {str(e)}')
        
        return logotipo
