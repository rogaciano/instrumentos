from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Categorias
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nova/', views.nova_categoria, name='nova_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/excluir/', views.excluir_categoria, name='excluir_categoria'),
    path('categorias/<int:pk>/', views.detalhe_categoria, name='detalhe_categoria'),

    # Modelos
    path('modelos/', views.lista_modelos, name='lista_modelos'),
    path('modelos/novo/', views.novo_modelo, name='novo_modelo'),
    path('modelos/<int:pk>/', views.detalhe_modelo, name='detalhe_modelo'),
    path('modelos/<int:pk>/editar/', views.editar_modelo, name='editar_modelo'),
    path('modelos/<int:pk>/excluir/', views.excluir_modelo, name='excluir_modelo'),

    # Instrumentos
    path('instrumentos/', views.lista_instrumentos, name='lista_instrumentos'),
    path('instrumentos/novo/', views.novo_instrumento, name='novo_instrumento'),
    path('instrumentos/<int:pk>/', views.detalhe_instrumento, name='detalhe_instrumento'),
    path('instrumentos/<int:pk>/editar/', views.editar_instrumento, name='editar_instrumento'),
    path('instrumentos/<int:pk>/excluir/', views.excluir_instrumento, name='excluir_instrumento'),
    path('instrumentos/<int:pk>/fotos/adicionar/', views.adicionar_fotos, name='adicionar_fotos'),
    path('instrumentos/fotos/<int:pk>/excluir/', views.excluir_foto, name='excluir_foto'),

    # Marcas
    path('marcas/', views.lista_marcas, name='lista_marcas'),
    path('marcas/nova/', views.nova_marca, name='nova_marca'),
    path('marcas/<int:pk>/', views.detalhe_marca, name='detalhe_marca'),
    path('marcas/<int:pk>/editar/', views.editar_marca, name='editar_marca'),
    path('marcas/<int:pk>/excluir/', views.excluir_marca, name='excluir_marca'),

    # APIs para cadastro rápido
    path('api/marcas/nova/', views.api_nova_marca, name='api_nova_marca'),
    path('api/categorias/nova/', views.api_nova_categoria, name='api_nova_categoria'),
    path('api/modelos/novo/', views.api_novo_modelo, name='api_novo_modelo'),
] 