from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Instrumento, Categoria, Modelo, FotoInstrumento, Marca
from .forms import CategoriaForm, ModeloForm, InstrumentoForm, MarcaForm
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import os
import json
import openai

# Create your views here.

@login_required
def home(request):
    total_instrumentos = Instrumento.objects.count()
    total_categorias = Categoria.objects.count()
    total_modelos = Modelo.objects.count()
    total_marcas = Marca.objects.count()
    
    # Calcula o valor total dos instrumentos (valor de mercado)
    valor_total_mercado = Instrumento.objects.aggregate(
        total=Sum('valor_mercado')
    )['total'] or 0
    
    context = {
        'total_instrumentos': total_instrumentos,
        'total_categorias': total_categorias,
        'total_modelos': total_modelos,
        'total_marcas': total_marcas,
        'valor_total_mercado': valor_total_mercado,
    }
    return render(request, 'instrumentos/home.html', context)


def lista_categorias(request):
    categorias = Categoria.objects.all()
    
    # Filtro por busca
    search = request.GET.get('search')
    if search:
        categorias = categorias.filter(
            Q(nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    return render(request, 'instrumentos/categorias/lista.html', {
        'categorias': categorias,
        'search': search
    })

def nova_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'instrumentos/categorias/form.html', {
        'form': form,
        'titulo': 'Nova Categoria'
    })

def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'instrumentos/categorias/form.html', {
        'form': form,
        'titulo': 'Editar Categoria'
    })

def excluir_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        if categoria.instrumento_set.exists():
            messages.error(request, 'Não é possível excluir uma categoria que possui instrumentos vinculados.')
        else:
            categoria.delete()
            messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('lista_categorias')
    
    return redirect('lista_categorias')

def detalhe_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    instrumentos = categoria.instrumento_set.all()
    return render(request, 'instrumentos/categorias/detalhe.html', {
        'categoria': categoria,
        'instrumentos': instrumentos
    })

# Views para Modelo
def lista_modelos(request):
    modelos = Modelo.objects.all()
    
    # Filtro por busca
    search = request.GET.get('search')
    if search:
        modelos = modelos.filter(
            Q(nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    return render(request, 'instrumentos/modelos/lista.html', {
        'modelos': modelos,
        'search': search
    })

def novo_modelo(request):
    if request.method == 'POST':
        form = ModeloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modelo criado com sucesso!')
            return redirect('lista_modelos')
    else:
        form = ModeloForm()
    
    return render(request, 'instrumentos/modelos/form.html', {
        'form': form,
        'titulo': 'Novo Modelo'
    })

def editar_modelo(request, pk):
    modelo = get_object_or_404(Modelo, pk=pk)
    
    if request.method == 'POST':
        form = ModeloForm(request.POST, instance=modelo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modelo atualizado com sucesso!')
            return redirect('lista_modelos')
    else:
        form = ModeloForm(instance=modelo)
    
    return render(request, 'instrumentos/modelos/form.html', {
        'form': form,
        'titulo': 'Editar Modelo'
    })

def detalhe_modelo(request, pk):
    modelo = get_object_or_404(Modelo, pk=pk)
    instrumentos = modelo.instrumento_set.all()
    return render(request, 'instrumentos/modelos/detalhe.html', {
        'modelo': modelo,
        'instrumentos': instrumentos
    })

def excluir_modelo(request, pk):
    modelo = get_object_or_404(Modelo, pk=pk)
    
    if request.method == 'POST':
        if modelo.instrumento_set.exists():
            messages.error(request, 'Não é possível excluir um modelo que possui instrumentos vinculados.')
        else:
            modelo.delete()
            messages.success(request, 'Modelo excluído com sucesso!')
        return redirect('lista_modelos')
    
    return redirect('lista_modelos')

@login_required
def lista_instrumentos(request):
    instrumentos = Instrumento.objects.all()
    
    # Filtros
    categoria = request.GET.get('categoria')
    marca = request.GET.get('marca')
    modelo = request.GET.get('modelo')
    estado = request.GET.get('estado')
    search = request.GET.get('search')
    
    if categoria:
        instrumentos = instrumentos.filter(categoria_id=categoria)
    if marca:
        instrumentos = instrumentos.filter(marca_id=marca)
    if modelo:
        instrumentos = instrumentos.filter(modelo_id=modelo)
    if estado:
        instrumentos = instrumentos.filter(estado_conservacao=estado)
    if search:
        instrumentos = instrumentos.filter(
            Q(nome__icontains=search) |
            Q(marca__nome__icontains=search) |
            Q(modelo__nome__icontains=search)
        )
    
    context = {
        'instrumentos': instrumentos,
        'categorias': Categoria.objects.all(),
        'marcas': Marca.objects.all(),
        'modelos': Modelo.objects.all(),
        'estados': Instrumento._meta.get_field('estado_conservacao').choices,
        'selected_categoria': categoria,
        'selected_marca': marca,
        'selected_modelo': modelo,
        'selected_estado': estado,
        'search': search,
    }
    return render(request, 'instrumentos/instrumentos/lista.html', context)

@login_required
def novo_instrumento(request):
    if request.method == 'POST':
        form = InstrumentoForm(request.POST)
        if form.is_valid():
            try:
                instrumento = form.save()
                
                # Processa as fotos
                for foto in request.FILES.getlist('fotos'):
                    FotoInstrumento.objects.create(
                        instrumento=instrumento,
                        imagem=foto
                    )
                
                messages.success(request, 'Instrumento cadastrado com sucesso!')
                return redirect('detalhe_instrumento', pk=instrumento.pk)
            except Exception as e:
                messages.error(request, f'Erro ao salvar instrumento: {str(e)}')
                print(f'Erro detalhado: {str(e)}')  # Para debug
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            print(f'Erros do formulário: {form.errors}')  # Para debug
    else:
        form = InstrumentoForm()
    
    return render(request, 'instrumentos/instrumentos/form.html', {
        'form': form,
        'titulo': 'Novo Instrumento'
    })

def editar_instrumento(request, pk):
    instrumento = get_object_or_404(Instrumento, pk=pk)
    
    if request.method == 'POST':
        form = InstrumentoForm(request.POST, instance=instrumento)
        if form.is_valid():
            instrumento = form.save()
            messages.success(request, 'Instrumento atualizado com sucesso!')
            return redirect('detalhe_instrumento', pk=instrumento.pk)
    else:
        # Formata a data para o formato esperado pelo input type="date"
        instrumento.data_aquisicao = instrumento.data_aquisicao.strftime('%Y-%m-%d')
        form = InstrumentoForm(instance=instrumento)
    
    return render(request, 'instrumentos/instrumentos/form.html', {
        'form': form,
        'titulo': 'Editar Instrumento',
        'instrumento': instrumento
    })

def detalhe_instrumento(request, pk):
    instrumento = get_object_or_404(Instrumento, pk=pk)
    fotos = instrumento.fotoinstrumento_set.all()
    return render(request, 'instrumentos/instrumentos/detalhe.html', {
        'instrumento': instrumento,
        'fotos': fotos
    })

def excluir_instrumento(request, pk):
    instrumento = get_object_or_404(Instrumento, pk=pk)
    
    if request.method == 'POST':
        instrumento.delete()
        messages.success(request, 'Instrumento excluído com sucesso!')
        return redirect('lista_instrumentos')
    
    return redirect('detalhe_instrumento', pk=pk)

def adicionar_fotos(request, pk):
    instrumento = get_object_or_404(Instrumento, pk=pk)
    
    if request.method == 'POST':
        for foto in request.FILES.getlist('fotos'):
            FotoInstrumento.objects.create(
                instrumento=instrumento,
                imagem=foto
            )
        messages.success(request, 'Fotos adicionadas com sucesso!')
        return redirect('detalhe_instrumento', pk=pk)
    
    return render(request, 'instrumentos/instrumentos/adicionar_fotos.html', {
        'instrumento': instrumento
    })

def excluir_foto(request, pk):
    foto = get_object_or_404(FotoInstrumento, pk=pk)
    instrumento_pk = foto.instrumento.pk
    
    if request.method == 'POST':
        foto.delete()
        messages.success(request, 'Foto excluída com sucesso!')
    
    return redirect('detalhe_instrumento', pk=instrumento_pk)

# Views para Marca
def lista_marcas(request):
    marcas = Marca.objects.all()
    
    # Filtros
    search = request.GET.get('search')
    pais = request.GET.get('pais')
    
    if search:
        marcas = marcas.filter(
            Q(nome__icontains=search) |
            Q(website__icontains=search)
        )
    if pais:
        marcas = marcas.filter(pais_origem__icontains=pais)
    
    # Lista única de países para o filtro
    paises = Marca.objects.values_list('pais_origem', flat=True).distinct()
    
    return render(request, 'instrumentos/marcas/lista.html', {
        'marcas': marcas,
        'paises': paises,
        'search': search,
        'selected_pais': pais
    })

def nova_marca(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca criada com sucesso!')
            return redirect('lista_marcas')
    else:
        form = MarcaForm()
    
    return render(request, 'instrumentos/marcas/form.html', {
        'form': form,
        'titulo': 'Nova Marca'
    })

def editar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    
    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca atualizada com sucesso!')
            return redirect('lista_marcas')
    else:
        form = MarcaForm(instance=marca)
    
    return render(request, 'instrumentos/marcas/form.html', {
        'form': form,
        'titulo': 'Editar Marca'
    })

def detalhe_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    instrumentos = marca.instrumento_set.all()
    return render(request, 'instrumentos/marcas/detalhe.html', {
        'marca': marca,
        'instrumentos': instrumentos
    })

def excluir_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    
    if request.method == 'POST':
        if marca.instrumento_set.exists():
            messages.error(request, 'Não é possível excluir uma marca que possui instrumentos vinculados.')
        else:
            marca.delete()
            messages.success(request, 'Marca excluída com sucesso!')
        return redirect('lista_marcas')
    
    return redirect('lista_marcas')

def api_nova_marca(request):
    if request.method == 'POST':
        try:
            marca = Marca.objects.create(
                nome=request.POST['nome'],
                pais_origem=request.POST.get('pais_origem', ''),
                website=request.POST.get('website', '')
            )
            return JsonResponse({
                'success': True,
                'marca': {
                    'id': marca.id,
                    'nome': marca.nome
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

def api_nova_categoria(request):
    if request.method == 'POST':
        try:
            categoria = Categoria.objects.create(
                nome=request.POST['nome'],
                descricao=request.POST.get('descricao', '')
            )
            return JsonResponse({
                'success': True,
                'categoria': {
                    'id': categoria.id,
                    'nome': categoria.nome
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

def api_novo_modelo(request):
    if request.method == 'POST':
        try:
            modelo = Modelo.objects.create(
                nome=request.POST['nome'],
                descricao=request.POST.get('descricao', '')
            )
            return JsonResponse({
                'success': True,
                'modelo': {
                    'id': modelo.id,
                    'nome': modelo.nome
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required
def ai_populate(request):
    if request.method == 'POST':
        selected_tables = request.POST.getlist('tables')
        
        if not selected_tables:
            messages.warning(request, 'Selecione pelo menos uma tabela para preencher.')
            return render(request, 'instrumentos/ai_populate.html', {'error': True})
        
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("API key não encontrada")

            client = openai.OpenAI(api_key=api_key)
            
            # Construir o prompt baseado nas tabelas selecionadas
            prompt_parts = []
            if 'categorias' in selected_tables:
                prompt_parts.append("1. 10 categorias de instrumentos (nome e descrição)")
            if 'marcas' in selected_tables:
                prompt_parts.append("2. 20 marcas famosas (nome, país de origem e website)")
            if 'modelos' in selected_tables:
                prompt_parts.append("3. 30 modelos populares (nome e descrição)")
            
            prompt = "Gere uma lista em formato JSON com dados de instrumentos musicais contendo:\n"
            prompt += "\n".join(prompt_parts)
            prompt += "\n\nFormato:\n{"
            
            if 'categorias' in selected_tables:
                prompt += '\n    "categorias": [{"nome": "", "descricao": ""}],'
            if 'marcas' in selected_tables:
                prompt += '\n    "marcas": [{"nome": "", "pais_origem": "", "website": ""}],'
            if 'modelos' in selected_tables:
                prompt += '\n    "modelos": [{"nome": "", "descricao": ""}],'
            
            prompt = prompt.rstrip(',') + "\n}"
            
            # Fazer a chamada para a API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em instrumentos musicais."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Processar a resposta
            data = json.loads(response.choices[0].message.content)
            
            # Criar os registros
            created_counts = {}
            skipped_counts = {}
            
            if 'categorias' in selected_tables and 'categorias' in data:
                count_created = 0
                count_skipped = 0
                for cat in data['categorias']:
                    try:
                        _, created = Categoria.objects.get_or_create(
                            nome=cat['nome'],
                            defaults={'descricao': cat['descricao']}
                        )
                        if created:
                            count_created += 1
                        else:
                            count_skipped += 1
                    except Exception as e:
                        count_skipped += 1
                created_counts['categorias'] = count_created
                skipped_counts['categorias'] = count_skipped
            
            if 'marcas' in selected_tables and 'marcas' in data:
                count_created = 0
                count_skipped = 0
                for marca in data['marcas']:
                    try:
                        _, created = Marca.objects.get_or_create(
                            nome=marca['nome'],
                            defaults={
                                'pais_origem': marca['pais_origem'],
                                'website': marca['website']
                            }
                        )
                        if created:
                            count_created += 1
                        else:
                            count_skipped += 1
                    except Exception as e:
                        count_skipped += 1
                created_counts['marcas'] = count_created
                skipped_counts['marcas'] = count_skipped
            
            if 'modelos' in selected_tables and 'modelos' in data:
                count_created = 0
                count_skipped = 0
                for modelo in data['modelos']:
                    try:
                        _, created = Modelo.objects.get_or_create(
                            nome=modelo['nome'],
                            defaults={'descricao': modelo['descricao']}
                        )
                        if created:
                            count_created += 1
                        else:
                            count_skipped += 1
                    except Exception as e:
                        count_skipped += 1
                created_counts['modelos'] = count_created
                skipped_counts['modelos'] = count_skipped
            
            # Criar mensagem de sucesso com detalhes
            success_msg = "Dados gerados com sucesso!\n"
            for table in created_counts.keys():
                success_msg += f"\n- {table.title()}: {created_counts[table]} criados"
                if skipped_counts[table] > 0:
                    success_msg += f" ({skipped_counts[table]} ignorados por já existirem)"
            
            messages.success(request, success_msg)
            
        except Exception as e:
            messages.error(request, f'Erro ao gerar dados: {str(e)}')
            return render(request, 'instrumentos/ai_populate.html', {'error': True})
        
        return redirect('ai_populate')
    
    return render(request, 'instrumentos/ai_populate.html')
