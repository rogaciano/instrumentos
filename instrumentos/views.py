import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal
from .models import Categoria, SubCategoria, Marca, Modelo, Instrumento, FotoInstrumento
from .forms import (
    CategoriaForm, SubCategoriaForm, MarcaForm, ModeloForm, 
    InstrumentoCreateForm, FotoInstrumentoFormSet
)
from .ai_helpers import setup_openai, generate_data
import json
import random
import logging
import re
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib.parse import urlparse

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

        # Totais de valores
        total_aquisicao = Instrumento.objects.aggregate(
            total=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F('preco'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                ),
                Decimal('0')
            )
        )['total']
        
        total_mercado = Instrumento.objects.aggregate(
            total=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F('valor_mercado'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                ),
                Decimal('0')
            )
        )['total']
        
        diferenca_total = total_mercado - total_aquisicao
        
        if total_aquisicao > 0:
            percentual_valorizacao = (diferenca_total / total_aquisicao) * Decimal('100')
        else:
            percentual_valorizacao = Decimal('0')

        context.update({
            'total_aquisicao': total_aquisicao,
            'total_mercado': total_mercado,
            'diferenca_total': diferenca_total,
            'percentual_valorizacao': percentual_valorizacao,
        })
        return context

def index(request):
    """View para a página inicial"""
    # Calcular valores financeiros
    instrumentos = Instrumento.objects.all()
    preco = instrumentos.aggregate(
        total=Coalesce(Sum('preco'), Decimal('0'))
    )['total']
    
    valor_mercado = instrumentos.aggregate(
        total=Coalesce(Sum('valor_mercado'), Decimal('0'))
    )['total']
    
    diferenca = valor_mercado - preco
    valorizacao = (diferenca / preco * 100) if preco > 0 else 0

    return render(request, 'instrumentos/index.html', {
        'total_instrumentos': instrumentos.count(),
        'total_marcas': Marca.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_subcategorias': SubCategoria.objects.count(),
        'preco': preco,
        'valor_mercado': valor_mercado,
        'diferenca': diferenca,
        'valorizacao': valorizacao,
        'instrumentos_recentes': instrumentos.order_by('-data_cadastro')[:5]
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

class InstrumentoDetailView(DetailView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_detail.html'
    context_object_name = 'instrumento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrumento = self.get_object()
        context['modelo_info'] = {
            'marca': instrumento.modelo.marca.nome,
            'subcategoria': instrumento.modelo.subcategoria.nome,
            'categoria': instrumento.modelo.subcategoria.categoria.nome
        }
        return context

class InstrumentoListView(ListView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_list.html'
    context_object_name = 'instrumentos'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'modelo__marca',
            'modelo__subcategoria__categoria'
        )

class InstrumentoCreateView(LoginRequiredMixin, CreateView):
    model = Instrumento
    form_class = InstrumentoCreateForm
    template_name = 'instrumentos/instrumento_form.html'
    success_url = reverse_lazy('instrumento_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['fotos_formset'] = FotoInstrumentoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['fotos_formset'] = FotoInstrumentoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        fotos_formset = context['fotos_formset']
        
        if fotos_formset.is_valid():
            self.object = form.save()
            fotos_formset.instance = self.object
            fotos_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class InstrumentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Instrumento
    form_class = InstrumentoCreateForm
    template_name = 'instrumentos/instrumento_form.html'
    success_url = reverse_lazy('instrumento_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['fotos_formset'] = FotoInstrumentoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['fotos_formset'] = FotoInstrumentoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        fotos_formset = context['fotos_formset']
        
        if fotos_formset.is_valid():
            self.object = form.save()
            fotos_formset.instance = self.object
            fotos_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class InstrumentoDeleteView(DeleteView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_confirm_delete.html'
    success_url = reverse_lazy('instrumento_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Instrumento excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

def foto_delete(request, instrumento_pk, pk):
    foto = get_object_or_404(FotoInstrumento, pk=pk)
    if request.method == 'POST':
        foto.delete()
        messages.success(request, 'Foto excluída com sucesso!')
    return redirect('instrumento_detail', pk=instrumento_pk)

def foto_update_descricao(request, instrumento_pk, pk):
    foto = get_object_or_404(FotoInstrumento, pk=pk)
    if request.method == 'POST':
        descricao = request.POST.get('descricao', '')
        foto.descricao = descricao
        foto.save()
        messages.success(request, 'Descrição atualizada com sucesso!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

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

def modelos_por_marca(request, marca_id):
    """API para retornar modelos de uma marca específica"""
    modelos = Modelo.objects.filter(marca_id=marca_id).values('id', 'nome')
    return JsonResponse(list(modelos), safe=False)

def modelo_create_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            nome = request.POST.get('nome')
            marca_id = request.POST.get('marca')
            descricao = request.POST.get('descricao')

            marca = get_object_or_404(Marca, pk=marca_id)
            modelo = Modelo.objects.create(
                nome=nome,
                marca=marca,
                descricao=descricao
            )

            return JsonResponse({
                'success': True,
                'modelo_id': modelo.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método não permitido'
    })

def generate_data(prompt, quantidade=10):
    """
    Gera dados usando a OpenAI API
    """
    try:
        # Configurar cliente OpenAI
        from openai import OpenAI
        client = OpenAI()
        
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
                Use APENAS categorias reais e comuns em lojas de música.
                Cada categoria deve ter:
                - nome: Nome único da categoria (ex: Cordas, Sopro, Percussão)
                - descricao: Descrição técnica e precisa da categoria
                
                Exemplo:
                [
                    {
                        "nome": "Cordas",
                        "descricao": "Instrumentos que produzem som através da vibração de cordas, incluindo cordas dedilhadas, friccionadas ou percutidas"
                    }
                ]
                """
                
                categorias_json = generate_data(prompt, quantidade=quantidade)
                try:
                    categorias_data = json.loads(categorias_json)
                    
                    created = 0
                    updated = 0
                    for cat_data in categorias_data:
                        cat, is_new = Categoria.objects.get_or_create(
                            nome=cat_data['nome']
                        )
                        cat.descricao = cat_data['descricao']
                        cat.save()
                        
                        if is_new:
                            created += 1
                        else:
                            updated += 1
                    
                    results['categorias'] = {
                        'created': created, 
                        'updated': updated,
                        'total_received': len(categorias_data)
                    }
                except json.JSONDecodeError as e:
                    results['categorias'] = {'error': str(e)}
            
            # Gerar Subcategorias
            if 'subcategorias' in tables:
                created = 0
                updated = 0
                for categoria in Categoria.objects.all():
                    prompt = f"""
                    Gere dados para subcategorias da categoria '{categoria.nome}' no formato JSON.
                    Use APENAS subcategorias que realmente pertencem a esta categoria principal.
                    Cada subcategoria deve ter:
                    - nome: Nome específico da subcategoria
                    - descricao: Descrição técnica e detalhada
                    
                    Para a categoria '{categoria.nome}', gere subcategorias específicas e coerentes.
                    Por exemplo, para "Cordas":
                    [
                        {{
                            "nome": "Violões",
                            "descricao": "Instrumentos de cordas dedilhadas com caixa acústica, incluindo violões clássicos e folk"
                        }}
                    ]
                    """
                    
                    subcategorias_json = generate_data(prompt, quantidade=quantidade)
                    try:
                        subcategorias_data = json.loads(subcategorias_json)
                        
                        for subcat_data in subcategorias_data:
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
                    results['subcategorias'] = {
                        'created': created, 
                        'updated': updated
                    }
            
            # Gerar Marcas
            if 'marcas' in tables:
                prompt = """
                Gere dados para marcas de instrumentos musicais no formato JSON.
                Inclua tanto marcas mundialmente famosas quanto marcas de médio porte.
                NÃO REPITA marcas já mencionadas.
                
                Cada marca deve ter:
                - nome: Nome oficial da marca
                - site: Site oficial da marca (URL completa e válida)
                - descricao: História detalhada da marca, incluindo ano de fundação e principais produtos
                - pais_origem: País onde a marca foi fundada
                
                Exemplos de marcas possíveis: Fender, Gibson, Yamaha, Ibanez, Roland, Korg, Pearl, Zildjian, Selmer, Buffet Crampon, etc.
                """
                
                marcas_json = generate_data(prompt, quantidade=quantidade)
                try:
                    marcas_data = json.loads(marcas_json)
                    
                    created = 0
                    updated = 0
                    marcas_processadas = set()
                    
                    for marca_data in marcas_data:
                        # Pular se já processamos esta marca
                        if marca_data['nome'] in marcas_processadas:
                            continue
                            
                        marca, is_new = Marca.objects.get_or_create(
                            nome=marca_data['nome']
                        )
                        marca.site = marca_data['site']
                        marca.descricao = marca_data['descricao']
                        marca.pais_origem = marca_data['pais_origem']
                        marca.save()
                        
                        marcas_processadas.add(marca_data['nome'])
                        
                        if is_new:
                            created += 1
                        else:
                            updated += 1
                    
                    results['marcas'] = {
                        'created': created, 
                        'updated': updated,
                        'total_received': len(marcas_data),
                        'unique_processed': len(marcas_processadas)
                    }
                except json.JSONDecodeError as e:
                    results['marcas'] = {'error': str(e)}
            
            # Gerar Modelos
            if 'modelos' in tables:
                if not SubCategoria.objects.exists():
                    messages.error(request, 'Não existem subcategorias. Por favor, gere subcategorias primeiro.')
                    results['modelos'] = {'error': 'Não existem subcategorias'}
                else:
                    created = 0
                    updated = 0
                    
                    for marca in Marca.objects.all():
                        # Para cada marca, vamos gerar modelos apenas para subcategorias apropriadas
                        for subcategoria in SubCategoria.objects.all():
                            prompt = f"""
                            Gere dados para modelos da marca '{marca.nome}' na subcategoria '{subcategoria.nome}' no formato JSON.
                            IMPORTANTE: Gere APENAS se a marca realmente produz instrumentos desta subcategoria.
                            Se a marca não produz instrumentos desta subcategoria, retorne array vazio [].
                            
                            Cada modelo deve ter:
                            - nome: Nome oficial e completo do modelo
                            - descricao: Descrição detalhada incluindo características técnicas
                            
                            Exemplo para Fender na subcategoria Guitarras Elétricas:
                            [
                                {{
                                    "nome": "Stratocaster American Professional II",
                                    "descricao": "Guitarra elétrica de corpo sólido com 3 captadores single-coil V-Mod II, ponte tremolo, braço em maple e corpo em alder."
                                }}
                            ]
                            """
                            
                            modelos_json = generate_data(prompt, quantidade=quantidade)
                            try:
                                modelos_data = json.loads(modelos_json)
                                
                                if modelos_data:  # Se a lista não estiver vazia
                                    for modelo_data in modelos_data:
                                        modelo, is_new = Modelo.objects.get_or_create(
                                            nome=modelo_data['nome'],
                                            marca=marca,
                                            defaults={
                                                'descricao': modelo_data['descricao'],
                                                'subcategoria': subcategoria
                                            }
                                        )
                                        
                                        if not is_new:
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
                        results['modelos'] = {
                            'created': created, 
                            'updated': updated
                        }
            
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
                        
                        instrumentos_json = generate_data(prompt, quantidade=1)
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
