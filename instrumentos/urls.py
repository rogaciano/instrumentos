from django.urls import path
from . import views
from .views import (
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    SubCategoriaListView, SubCategoriaCreateView, SubCategoriaUpdateView, SubCategoriaDeleteView,
    MarcaListView, MarcaCreateView, MarcaUpdateView, MarcaDeleteView,
    ModeloListView, ModeloCreateView, ModeloUpdateView, ModeloDeleteView,
    InstrumentoListView, InstrumentoDetailView, InstrumentoCreateView, InstrumentoUpdateView, InstrumentoDeleteView,
    FotoCreateView, FotoDeleteView
)

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('inicial/', views.home, name='inicial'),

    # Categorias
    path('categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nova/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/excluir/', CategoriaDeleteView.as_view(), name='categoria_delete'),

    # SubCategorias
    path('subcategorias/', SubCategoriaListView.as_view(), name='subcategoria_list'),
    path('subcategorias/nova/', SubCategoriaCreateView.as_view(), name='subcategoria_create'),
    path('subcategorias/<int:pk>/editar/', SubCategoriaUpdateView.as_view(), name='subcategoria_update'),
    path('subcategorias/<int:pk>/excluir/', SubCategoriaDeleteView.as_view(), name='subcategoria_delete'),

    # Marcas
    path('marcas/', MarcaListView.as_view(), name='marca_list'),
    path('marcas/nova/', MarcaCreateView.as_view(), name='marca_create'),
    path('marcas/<int:pk>/editar/', MarcaUpdateView.as_view(), name='marca_update'),
    path('marcas/<int:pk>/excluir/', MarcaDeleteView.as_view(), name='marca_delete'),

    # Modelos
    path('modelos/', ModeloListView.as_view(), name='modelo_list'),
    path('modelos/novo/', ModeloCreateView.as_view(), name='modelo_create'),
    path('modelos/<int:pk>/editar/', ModeloUpdateView.as_view(), name='modelo_update'),
    path('modelos/<int:pk>/excluir/', ModeloDeleteView.as_view(), name='modelo_delete'),

    # Instrumentos
    path('instrumentos/', InstrumentoListView.as_view(), name='instrumento_list'),
    path('instrumentos/novo/', InstrumentoCreateView.as_view(), name='instrumento_create'),
    path('instrumentos/<int:pk>/', InstrumentoDetailView.as_view(), name='instrumento_detail'),
    path('instrumentos/<int:pk>/editar/', InstrumentoUpdateView.as_view(), name='instrumento_update'),
    path('instrumentos/<int:pk>/excluir/', InstrumentoDeleteView.as_view(), name='instrumento_delete'),

    # Fotos
    path('instrumentos/<int:instrumento_id>/fotos/nova/', FotoCreateView.as_view(), name='foto_create'),
    path('fotos/<int:pk>/excluir/', FotoDeleteView.as_view(), name='foto_delete'),

    # API
    path('api/modelos-por-marca/<int:marca_id>/', views.modelos_por_marca, name='api_modelos_por_marca'),

    # AI Populate
    path('ai-populate/', views.ai_populate_view, name='ai_populate'),
]