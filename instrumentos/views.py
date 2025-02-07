import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Instrumento, Categoria, Modelo, FotoInstrumento, Marca, SubCategoria
from .forms import CategoriaForm, ModeloForm, InstrumentoForm, MarcaForm, SubCategoriaForm
import json
import openai
from .ai_helpers import (
    setup_openai,
    generate_categorias,
    generate_subcategorias,
    generate_marcas,
    generate_modelos
)
import logging

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def home(request):
    return render(request, 'instrumentos/home.html')

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'instrumentos/categoria_list.html'
    context_object_name = 'categorias'
    ordering = ['nome']

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

class SubCategoriaListView(ListView):
    model = SubCategoria
    template_name = 'instrumentos/subcategoria_list.html'
    context_object_name = 'subcategorias'
    ordering = ['categoria__nome', 'nome']

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

class MarcaListView(ListView):
    model = Marca
    template_name = 'instrumentos/marca_list.html'
    context_object_name = 'marcas'
    ordering = ['nome']

class MarcaCreateView(CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'instrumentos/marca_form.html'
    success_url = reverse_lazy('marca_list')

    def form_valid(self, form):
        messages.success(self.request, 'Marca criada com sucesso!')
        return super().form_valid(form)

class MarcaUpdateView(UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'instrumentos/marca_form.html'
    success_url = reverse_lazy('marca_list')

    def form_valid(self, form):
        messages.success(self.request, 'Marca atualizada com sucesso!')
        return super().form_valid(form)

class MarcaDeleteView(DeleteView):
    model = Marca
    template_name = 'instrumentos/marca_confirm_delete.html'
    success_url = reverse_lazy('marca_list')

    def delete(self, request, *args, **kwargs):
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

class InstrumentoListView(ListView):
    model = Instrumento
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
        return queryset

class InstrumentoDetailView(DetailView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_detail.html'
    context_object_name = 'instrumento'

class InstrumentoCreateView(CreateView):
    model = Instrumento
    form_class = InstrumentoForm
    template_name = 'instrumentos/instrumento_form.html'
    success_url = reverse_lazy('instrumento_list')

    def form_valid(self, form):
        messages.success(self.request, 'Instrumento criado com sucesso!')
        return super().form_valid(form)

class InstrumentoUpdateView(UpdateView):
    model = Instrumento
    form_class = InstrumentoForm
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
        form.instance.instrumento_id = self.kwargs['pk']
        messages.success(self.request, 'Foto adicionada com sucesso!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('instrumento_detail', kwargs={'pk': self.kwargs['pk']})

class FotoDeleteView(DeleteView):
    model = FotoInstrumento
    template_name = 'instrumentos/foto_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('instrumento_detail', kwargs={'pk': self.object.instrumento.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Foto excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

def modelos_por_marca(request, marca_id):
    """API para retornar modelos de uma marca específica"""
    modelos = Modelo.objects.filter(marca_id=marca_id).values('id', 'nome')
    return JsonResponse(list(modelos), safe=False)

def ai_populate_view(request):
    results = {}
    
    if request.method == 'POST':
        try:
            # Configurar OpenAI com a chave do settings.py
            setup_openai()
            
            # Obter parâmetros
            tables = request.POST.getlist('tables')
            quantidade = int(request.POST.get('quantidade', 10))
            
            # Gerar Categorias
            if 'categorias' in tables:
                categorias_json = generate_categorias(quantidade)
                categorias_data = json.loads(categorias_json)
                
                generated = 0
                skipped = 0
                for cat in categorias_data:
                    _, created = Categoria.objects.get_or_create(
                        nome=cat['nome'],
                        defaults={'descricao': cat['descricao']}
                    )
                    if created:
                        generated += 1
                    else:
                        skipped += 1
                
                results['categorias'] = {'generated': generated, 'skipped': skipped}
            
            # Gerar Subcategorias
            if 'subcategorias' in tables:
                generated = 0
                skipped = 0
                for categoria in Categoria.objects.all():
                    subcategorias_json = generate_subcategorias(quantidade, categoria)
                    subcategorias_data = json.loads(subcategorias_json)
                    
                    for subcat in subcategorias_data:
                        _, created = SubCategoria.objects.get_or_create(
                            nome=subcat['nome'],
                            categoria=categoria,
                            defaults={'descricao': subcat['descricao']}
                        )
                        if created:
                            generated += 1
                        else:
                            skipped += 1
                
                results['subcategorias'] = {'generated': generated, 'skipped': skipped}
            
            # Gerar Marcas
            if 'marcas' in tables:
                marcas_json = generate_marcas(quantidade)
                marcas_data = json.loads(marcas_json)
                
                generated = 0
                skipped = 0
                for marca in marcas_data:
                    _, created = Marca.objects.get_or_create(
                        nome=marca['nome'],
                        defaults={
                            'pais_origem': marca['pais_origem'],
                            'website': marca['website']
                        }
                    )
                    if created:
                        generated += 1
                    else:
                        skipped += 1
                
                results['marcas'] = {'generated': generated, 'skipped': skipped}
            
            # Gerar Modelos
            if 'modelos' in tables:
                generated = 0
                skipped = 0
                for marca in Marca.objects.all():
                    modelos_json = generate_modelos(quantidade, marca)
                    modelos_data = json.loads(modelos_json)
                    
                    for modelo in modelos_data:
                        # Encontrar a subcategoria pelo nome
                        try:
                            subcategoria = SubCategoria.objects.get(nome=modelo['subcategoria'])
                            _, created = Modelo.objects.get_or_create(
                                nome=modelo['nome'],
                                marca=marca,
                                defaults={
                                    'descricao': modelo['descricao'],
                                    'subcategoria': subcategoria
                                }
                            )
                            if created:
                                generated += 1
                            else:
                                skipped += 1
                        except SubCategoria.DoesNotExist:
                            skipped += 1
                            logger.warning(f"Subcategoria '{modelo['subcategoria']}' não encontrada")
                
                results['modelos'] = {'generated': generated, 'skipped': skipped}
            
            messages.success(request, 'Dados gerados com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao gerar dados: {str(e)}')
    
    return render(request, 'instrumentos/ai_populate.html', {'results': results})
