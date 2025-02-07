import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Instrumento, Categoria, Modelo, FotoInstrumento, Marca, SubCategoria
from .forms import CategoriaForm, ModeloForm, InstrumentoCreateForm, MarcaForm, SubCategoriaForm
import json
import openai
from .ai_helpers import (
    setup_openai,
    generate_categorias,
    generate_subcategorias,
    generate_marcas,
    generate_modelos,
    generate_instrumentos,
    generate_logo_url
)
import logging
from decimal import Decimal
from django.utils import timezone
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib.parse import urlparse
import random

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def home(request):
    return render(request, 'instrumentos/home.html')

class HomeView(TemplateView):
    template_name = 'instrumentos/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Total de instrumentos
        context['total_instrumentos'] = Instrumento.objects.count()

        # Total de categorias com instrumentos
        context['total_categorias'] = Categoria.objects.annotate(
            total_instrumentos=Count('subcategorias__modelos__instrumento', distinct=True)
        ).filter(total_instrumentos__gt=0).count()

        # Total de subcategorias com instrumentos
        context['total_subcategorias'] = SubCategoria.objects.annotate(
            total_instrumentos=Count('modelos__instrumento', distinct=True)
        ).filter(total_instrumentos__gt=0).count()

        # Total de marcas com instrumentos
        context['total_marcas'] = Marca.objects.annotate(
            total_instrumentos=Count('modelos__instrumento', distinct=True)
        ).filter(total_instrumentos__gt=0).count()

        # Estatísticas detalhadas
        context['categorias'] = Categoria.objects.annotate(
            total_instrumentos=Count('subcategorias__modelos__instrumento', distinct=True)
        ).filter(total_instrumentos__gt=0).order_by('-total_instrumentos')

        context['subcategorias'] = SubCategoria.objects.annotate(
            total_instrumentos=Count('modelos__instrumento', distinct=True)
        ).filter(total_instrumentos__gt=0).order_by('-total_instrumentos')

        context['marcas'] = Marca.objects.annotate(
            total_instrumentos=Count('modelos__instrumento', distinct=True)
        ).filter(total_instrumentos__gt=0).order_by('-total_instrumentos')

        return context

def index(request):
    """View para a página inicial"""
    return render(request, 'instrumentos/index.html', {
        'total_instrumentos': Instrumento.objects.count(),
        'total_marcas': Marca.objects.count(),
        'total_modelos': Modelo.objects.count(),
        'instrumentos_recentes': Instrumento.objects.order_by('-data_cadastro')[:5]
    })

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'instrumentos/categoria_list.html'
    context_object_name = 'categorias'
    ordering = ['nome']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por texto (nome ou descrição)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(nome__icontains=q) | queryset.filter(descricao__icontains=q)
        
        return queryset.order_by('nome')

class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'instrumentos/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)

class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'instrumentos/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)

class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = 'instrumentos/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Categoria excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

class CategoriaDetailView(DetailView):
    model = Categoria
    template_name = 'instrumentos/categoria_detail.html'
    context_object_name = 'categoria'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ordenar subcategorias por nome
        context['subcategorias'] = self.object.subcategorias.order_by('nome')
        return context

class SubCategoriaListView(ListView):
    model = SubCategoria
    template_name = 'instrumentos/subcategoria_list.html'
    context_object_name = 'subcategorias'
    ordering = ['categoria__nome', 'nome']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por texto (nome ou descrição)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | 
                Q(descricao__icontains=q) |
                Q(categoria__nome__icontains=q)
            )
        
        # Filtro por categoria
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        return queryset.select_related('categoria').order_by('categoria__nome', 'nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.order_by('nome')
        return context

class SubCategoriaCreateView(CreateView):
    model = SubCategoria
    form_class = SubCategoriaForm
    template_name = 'instrumentos/subcategoria_form.html'
    success_url = reverse_lazy('subcategoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Subcategoria criada com sucesso!')
        return super().form_valid(form)

class SubCategoriaUpdateView(UpdateView):
    model = SubCategoria
    form_class = SubCategoriaForm
    template_name = 'instrumentos/subcategoria_form.html'
    success_url = reverse_lazy('subcategoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Subcategoria atualizada com sucesso!')
        return super().form_valid(form)

class SubCategoriaDeleteView(DeleteView):
    model = SubCategoria
    template_name = 'instrumentos/subcategoria_confirm_delete.html'
    success_url = reverse_lazy('subcategoria_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Subcategoria excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

class SubCategoriaDetailView(DetailView):
    model = SubCategoria
    template_name = 'instrumentos/subcategoria_detail.html'
    context_object_name = 'subcategoria'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ordenar modelos por nome
        context['modelos'] = self.object.modelos.select_related('marca').order_by('marca__nome', 'nome')
        return context

class MarcaListView(ListView):
    model = Marca
    template_name = 'instrumentos/marca_list.html'
    context_object_name = 'marcas'
    ordering = ['nome']
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            return queryset.filter(
                Q(nome__icontains=q) |
                Q(descricao__icontains=q) |
                Q(pais_origem__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context

class MarcaCreateView(LoginRequiredMixin, CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'instrumentos/marca_form.html'
    success_url = reverse_lazy('marca_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Marca criada com sucesso!')
        return super().form_valid(form)

class MarcaUpdateView(LoginRequiredMixin, UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'instrumentos/marca_form.html'
    success_url = reverse_lazy('marca_list')
    
    def form_valid(self, form):
        # Se temos um novo logotipo e já existe um antigo
        if form.cleaned_data.get('logotipo') and self.object.logotipo:
            try:
                # Guardar o caminho do arquivo antigo
                old_logo_path = self.object.logotipo.path
                
                # Salvar o novo logotipo
                response = super().form_valid(form)
                
                try:
                    # Tentar deletar o arquivo antigo
                    if os.path.exists(old_logo_path):
                        os.remove(old_logo_path)
                except (OSError, PermissionError) as e:
                    # Se não conseguir deletar agora, logar o erro mas não falhar
                    logger.warning(f"Não foi possível deletar o logotipo antigo: {str(e)}")
                
                return response
            except Exception as e:
                messages.error(self.request, f"Erro ao atualizar logotipo: {str(e)}")
                return super().form_invalid(form)
        
        return super().form_valid(form)

class MarcaDeleteView(LoginRequiredMixin, DeleteView):
    model = Marca
    template_name = 'instrumentos/marca_confirm_delete.html'
    success_url = reverse_lazy('marca_list')
    
    def delete(self, request, *args, **kwargs):
        marca = self.get_object()
        # Deletar logotipo se existir
        if marca.logotipo:
            marca.logotipo.delete(save=False)
        messages.success(request, 'Marca excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

class ModeloListView(ListView):
    model = Modelo
    template_name = 'instrumentos/modelo_list.html'
    context_object_name = 'modelos'
    paginate_by = 12  # Paginação similar a e-commerce
    ordering = ['marca__nome', 'nome']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por texto (nome do modelo)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(nome__icontains=q)
        
        # Filtro por marca
        marca = self.request.GET.get('marca')
        if marca:
            queryset = queryset.filter(marca_id=marca)
            
        # Filtro por categoria
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(subcategoria__categoria_id=categoria)
            
        # Filtro por subcategoria
        subcategoria = self.request.GET.get('subcategoria')
        if subcategoria:
            queryset = queryset.filter(subcategoria_id=subcategoria)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar listas para os filtros
        context['marcas'] = Marca.objects.all().order_by('nome')
        context['categorias'] = Categoria.objects.all().order_by('nome')
        context['subcategorias'] = SubCategoria.objects.all().order_by('categoria__nome', 'nome')
        
        # Manter filtros selecionados
        context['selected_marca'] = self.request.GET.get('marca')
        context['selected_categoria'] = self.request.GET.get('categoria')
        context['selected_subcategoria'] = self.request.GET.get('subcategoria')
        context['search_query'] = self.request.GET.get('q')
        
        return context

class ModeloCreateView(CreateView):
    model = Modelo
    form_class = ModeloForm
    template_name = 'instrumentos/modelo_form.html'
    success_url = reverse_lazy('modelo_list')

    def form_valid(self, form):
        messages.success(self.request, 'Modelo criado com sucesso!')
        return super().form_valid(form)

class ModeloUpdateView(UpdateView):
    model = Modelo
    form_class = ModeloForm
    template_name = 'instrumentos/modelo_form.html'
    success_url = reverse_lazy('modelo_list')

    def form_valid(self, form):
        messages.success(self.request, 'Modelo atualizado com sucesso!')
        return super().form_valid(form)

class ModeloDeleteView(DeleteView):
    model = Modelo
    template_name = 'instrumentos/modelo_confirm_delete.html'
    success_url = reverse_lazy('modelo_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Modelo excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

class ModeloDetailView(DetailView):
    model = Modelo
    template_name = 'instrumentos/modelo_detail.html'
    context_object_name = 'modelo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ordenar instrumentos por número de série e incluir fotos
        context['instrumentos'] = self.object.instrumento_set.prefetch_related(
            'fotoinstrumento_set'
        ).order_by('numero_serie')
        return context

class InstrumentoListView(ListView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_list.html'
    context_object_name = 'instrumentos_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            return queryset.filter(
                Q(codigo__icontains=q) |
                Q(modelo__nome__icontains=q) |
                Q(modelo__marca__nome__icontains=q) |
                Q(subcategoria__nome__icontains=q)
            )
        return queryset.order_by('-data_cadastro')

class InstrumentoDetailView(DetailView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_detail.html'
    context_object_name = 'instrumento'

class InstrumentoCreateView(CreateView):
    model = Instrumento
    form_class = InstrumentoCreateForm
    template_name = 'instrumentos/instrumento_form.html'

    def form_valid(self, form):
        # Primeiro salva o instrumento
        response = super().form_valid(form)
        
        # Processa as fotos
        fotos = self.request.FILES.getlist('fotos')
        for foto in fotos:
            # Valida tamanho
            if foto.size > 5 * 1024 * 1024:  # 5MB
                form.add_error('fotos', f'A foto {foto.name} é muito grande. O tamanho máximo é 5MB.')
                return self.form_invalid(form)
            
            # Valida tipo
            import imghdr
            if not imghdr.what(foto):
                form.add_error('fotos', f'O arquivo {foto.name} não é uma imagem válida.')
                return self.form_invalid(form)
            
            # Salva a foto
            FotoInstrumento.objects.create(
                instrumento=self.object,
                imagem=foto
            )
        
        messages.success(self.request, 'Instrumento criado com sucesso!')
        return response

    def get_success_url(self):
        return reverse_lazy('instrumento_detail', kwargs={'pk': self.object.pk})

class InstrumentoUpdateView(UpdateView):
    model = Instrumento
    form_class = InstrumentoCreateForm
    template_name = 'instrumentos/instrumento_form.html'
    success_url = reverse_lazy('instrumento_list')

    def form_valid(self, form):
        messages.success(self.request, 'Instrumento atualizado com sucesso!')
        return super().form_valid(form)

class InstrumentoDeleteView(DeleteView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_confirm_delete.html'
    success_url = reverse_lazy('instrumento_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Instrumento excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

class FotoCreateView(CreateView):
    model = FotoInstrumento
    fields = ['imagem', 'descricao']
    template_name = 'instrumentos/foto_form.html'

    def form_valid(self, form):
        instrumento = get_object_or_404(Instrumento, pk=self.kwargs['instrumento_pk'])
        form.instance.instrumento = instrumento
        messages.success(self.request, 'Foto adicionada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instrumento'] = get_object_or_404(Instrumento, pk=self.kwargs['instrumento_pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('instrumento_detail', kwargs={'pk': self.kwargs['instrumento_pk']})

class FotoDeleteView(DeleteView):
    model = FotoInstrumento
    template_name = 'instrumentos/foto_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('instrumento_detail', kwargs={'pk': self.kwargs['instrumento_pk']})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Foto excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

def modelos_por_marca(request, marca_id):
    """API para retornar modelos de uma marca específica"""
    modelos = Modelo.objects.filter(marca_id=marca_id).values('id', 'nome')
    return JsonResponse(list(modelos), safe=False)

def generate_data(prompt):
    """
    Gera dados usando a OpenAI API
    """
    try:
        # Configurar cliente OpenAI
        client = openai.OpenAI()
        
        # Fazer a chamada para a API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em gerar dados para um sistema de cadastro de instrumentos musicais. Gere apenas o JSON solicitado, sem explicações adicionais."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extrair o JSON da resposta
        json_response = response.choices[0].message.content.strip()
        
        # Se a resposta não começa com [, tentar encontrar o JSON
        if not json_response.startswith('['):
            # Procurar por [ e ]
            start = json_response.find('[')
            end = json_response.rfind(']')
            
            if start != -1 and end != -1:
                json_response = json_response[start:end+1]
            else:
                raise ValueError("Resposta não contém JSON válido")
        
        return json_response
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados via OpenAI: {str(e)}")
        raise

def ai_populate_view(request):
    results = {}
    
    if request.method == 'POST':
        try:
            # Configurar OpenAI
            setup_openai()
            
            # Obter parâmetros
            tables = request.POST.getlist('tables')
            quantidade = int(request.POST.get('quantidade', 10))
            
            # Gerar Categorias
            if 'categorias' in tables:
                prompt = """
                Gere dados para categorias de instrumentos musicais no formato JSON.
                Cada categoria deve ter:
                - nome: Nome da categoria
                - descricao: Breve descrição da categoria
                
                Exemplo:
                [
                    {
                        "nome": "Cordas",
                        "descricao": "Instrumentos que produzem som através da vibração de cordas"
                    }
                ]
                """
                
                categorias_json = generate_data(prompt)
                try:
                    categorias_data = json.loads(categorias_json)
                    
                    created = 0
                    updated = 0
                    for cat_data in categorias_data[:quantidade]:
                        cat, is_new = Categoria.objects.get_or_create(
                            nome=cat_data['nome']
                        )
                        cat.descricao = cat_data['descricao']
                        cat.save()
                        
                        if is_new:
                            created += 1
                        else:
                            updated += 1
                    
                    results['categorias'] = {'created': created, 'updated': updated}
                except json.JSONDecodeError as e:
                    results['categorias'] = {'error': str(e)}
            
            # Gerar Subcategorias
            if 'subcategorias' in tables:
                created = 0
                updated = 0
                for categoria in Categoria.objects.all():
                    prompt = f"""
                    Gere dados para subcategorias da categoria '{categoria.nome}' no formato JSON.
                    Cada subcategoria deve ter:
                    - nome: Nome da subcategoria
                    - descricao: Breve descrição da subcategoria
                    
                    Exemplo:
                    [
                        {{
                            "nome": "Violões",
                            "descricao": "Violões acústicos e clássicos"
                        }}
                    ]
                    """
                    
                    subcategorias_json = generate_data(prompt)
                    try:
                        subcategorias_data = json.loads(subcategorias_json)
                        
                        for subcat_data in subcategorias_data[:quantidade]:
                            subcat, is_new = SubCategoria.objects.get_or_create(
                                nome=subcat_data['nome'],
                                categoria=categoria
                            )
                            subcat.descricao = subcat_data['descricao']
                            subcat.save()
                            
                            if is_new:
                                created += 1
                            else:
                                updated += 1
                    except json.JSONDecodeError as e:
                        results['subcategorias'] = {'error': str(e)}
                        break
                
                if 'subcategorias' not in results:
                    results['subcategorias'] = {'created': created, 'updated': updated}
            
            # Gerar Marcas
            if 'marcas' in tables:
                prompt = """
                Gere dados para marcas de instrumentos musicais no formato JSON.
                Cada marca deve ter:
                - nome: Nome da marca
                - site: Site oficial da marca (URL completa)
                - descricao: Breve descrição da marca e sua história
                - pais_origem: País de origem da marca
                
                Exemplo:
                [
                    {
                        "nome": "Fender",
                        "site": "https://www.fender.com",
                        "descricao": "Fundada em 1946, a Fender é uma das mais icônicas fabricantes de guitarras e baixos.",
                        "pais_origem": "Estados Unidos"
                    }
                ]
                """
                
                marcas_json = generate_data(prompt)
                try:
                    marcas_data = json.loads(marcas_json)
                    
                    created = 0
                    updated = 0
                    for marca_data in marcas_data[:quantidade]:
                        marca, is_new = Marca.objects.get_or_create(
                            nome=marca_data['nome']
                        )
                        marca.site = marca_data['site']
                        marca.descricao = marca_data['descricao']
                        marca.pais_origem = marca_data['pais_origem']
                        marca.save()
                        
                        if is_new:
                            created += 1
                        else:
                            updated += 1
                    
                    results['marcas'] = {'created': created, 'updated': updated}
                except json.JSONDecodeError as e:
                    results['marcas'] = {'error': str(e)}
            
            # Gerar Modelos
            if 'modelos' in tables:
                # Verificar se existem subcategorias
                if not SubCategoria.objects.exists():
                    messages.error(request, 'Não existem subcategorias. Por favor, gere subcategorias primeiro.')
                    results['modelos'] = {'error': 'Não existem subcategorias'}
                else:
                    created = 0
                    updated = 0
                    
                    # Pegar todas as subcategorias disponíveis
                    subcategorias = list(SubCategoria.objects.all())
                    
                    for marca in Marca.objects.all():
                        prompt = f"""
                        Gere dados para modelos de instrumentos da marca '{marca.nome}' no formato JSON.
                        Cada modelo deve ter:
                        - nome: Nome do modelo
                        - descricao: Breve descrição do modelo
                        
                        Exemplo:
                        [
                            {{
                                "nome": "Stratocaster",
                                "descricao": "A lendária guitarra que definiu o som do rock"
                            }}
                        ]
                        """
                        
                        modelos_json = generate_data(prompt)
                        try:
                            modelos_data = json.loads(modelos_json)
                            
                            for modelo_data in modelos_data[:quantidade]:
                                # Escolher uma subcategoria aleatória
                                subcategoria = random.choice(subcategorias)
                                
                                modelo, is_new = Modelo.objects.get_or_create(
                                    nome=modelo_data['nome'],
                                    marca=marca,
                                    defaults={
                                        'descricao': modelo_data['descricao'],
                                        'subcategoria': subcategoria
                                    }
                                )
                                
                                if not is_new:
                                    # Atualizar dados existentes
                                    modelo.descricao = modelo_data['descricao']
                                    modelo.subcategoria = subcategoria
                                    modelo.save()
                                
                                if is_new:
                                    created += 1
                                else:
                                    updated += 1
                        except json.JSONDecodeError as e:
                            results['modelos'] = {'error': str(e)}
                            break
                    
                    if 'modelos' not in results:
                        results['modelos'] = {'created': created, 'updated': updated}
            
            # Gerar Instrumentos
            if 'instrumentos' in tables:
                # Verificar se existem modelos
                if not Modelo.objects.exists():
                    messages.error(request, 'Não existem modelos. Por favor, gere modelos primeiro.')
                    results['instrumentos'] = {'error': 'Não existem modelos'}
                else:
                    created = 0
                    updated = 0
                    
                    # Pegar todos os modelos disponíveis
                    modelos = list(Modelo.objects.all())
                    
                    # Gerar código sequencial
                    ultimo_codigo = Instrumento.objects.order_by('-codigo').first()
                    if ultimo_codigo:
                        ultimo_numero = int(ultimo_codigo.codigo.replace('INST', ''))
                    else:
                        ultimo_numero = 0
                    
                    for _ in range(quantidade):
                        # Escolher um modelo aleatório
                        modelo = random.choice(modelos)
                        
                        prompt = f"""
                        Gere um único instrumento musical do modelo '{modelo.nome}' da marca '{modelo.marca.nome}' no formato JSON.
                        Use este formato exato:
                        {{
                            "numero_serie": "ABC123456",
                            "ano_fabricacao": 2020,
                            "preco": 1999.99,
                            "valor_mercado": 2100.00,
                            "estado_conservacao": "excelente",
                            "status": "disponivel"
                        }}
                        
                        Regras:
                        1. numero_serie: alfanumérico, único
                        2. ano_fabricacao: entre 1950 e 2024
                        3. preco: entre 500 e 50000
                        4. valor_mercado: próximo ao preço
                        5. estado_conservacao: novo, excelente, muito_bom, bom, regular ou ruim
                        6. status: disponivel, vendido, reservado ou manutencao
                        """
                        
                        instrumentos_json = generate_data(prompt)
                        try:
                            # Limpar a resposta
                            json_str = instrumentos_json.strip()
                            if json_str.startswith('```json'):
                                json_str = json_str[7:]
                            if json_str.endswith('```'):
                                json_str = json_str[:-3]
                            json_str = json_str.strip()
                            
                            # Se for uma lista, pegar o primeiro item
                            instrumento_data = json.loads(json_str)
                            if isinstance(instrumento_data, list):
                                instrumento_data = instrumento_data[0]
                            
                            # Gerar código sequencial
                            ultimo_numero += 1
                            codigo = f"INST{ultimo_numero:04d}"
                            
                            instrumento, is_new = Instrumento.objects.get_or_create(
                                codigo=codigo,
                                defaults={
                                    'modelo': modelo,
                                    'numero_serie': instrumento_data['numero_serie'],
                                    'ano_fabricacao': instrumento_data['ano_fabricacao'],
                                    'preco': instrumento_data['preco'],
                                    'valor_mercado': instrumento_data.get('valor_mercado'),
                                    'estado_conservacao': instrumento_data['estado_conservacao'],
                                    'status': instrumento_data['status']
                                }
                            )
                            
                            if not is_new:
                                # Atualizar dados existentes
                                instrumento.modelo = modelo
                                instrumento.numero_serie = instrumento_data['numero_serie']
                                instrumento.ano_fabricacao = instrumento_data['ano_fabricacao']
                                instrumento.preco = instrumento_data['preco']
                                instrumento.valor_mercado = instrumento_data.get('valor_mercado')
                                instrumento.estado_conservacao = instrumento_data['estado_conservacao']
                                instrumento.status = instrumento_data['status']
                                instrumento.save()
                            
                            if is_new:
                                created += 1
                            else:
                                updated += 1
                        except json.JSONDecodeError as e:
                            logger.error(f"Erro ao decodificar JSON: {str(e)}")
                            logger.error(f"JSON recebido: {instrumentos_json}")
                            results['instrumentos'] = {'error': f"Erro ao decodificar JSON: {str(e)}"}
                            break
                        except Exception as e:
                            logger.error(f"Erro ao gerar instrumento: {str(e)}")
                            logger.error(f"JSON recebido: {instrumentos_json}")
                            results['instrumentos'] = {'error': f"Erro ao gerar instrumento: {str(e)}"}
                            break
                    
                    if 'instrumentos' not in results:
                        results['instrumentos'] = {'created': created, 'updated': updated}
            
            # Mensagens de sucesso
            total_created = sum(r.get('created', 0) for r in results.values() if isinstance(r, dict) and 'error' not in r)
            total_updated = sum(r.get('updated', 0) for r in results.values() if isinstance(r, dict) and 'error' not in r)
            
            if total_created:
                messages.success(request, f'{total_created} registros criados com sucesso!')
            if total_updated:
                messages.info(request, f'{total_updated} registros atualizados!')
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados: {str(e)}")
            messages.error(request, f'Erro ao gerar dados: {str(e)}')
    
    return render(request, 'instrumentos/ai_populate.html', {'results': results})
