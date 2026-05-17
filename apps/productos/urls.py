from django.urls import path

from apps.productos import views

urlpatterns = [

    path(
        '',
        views.lista_productos,
        name='lista_productos'
    ),
    
    path(
        'crear/',
        views.crear_producto,
        name='crear_producto'
    ),
    
    path(
    'editar/<int:producto_id>/',
    views.editar_producto,
    name='editar_producto'
    ),
    
    path(
    'disponibilidad/<int:producto_id>/',
    views.toggle_disponibilidad_producto,
    name='toggle_disponibilidad_producto'
    ),
    
    path(
    'categorias/',
    views.lista_categorias,
    name='lista_categorias'
    ),

    path(
        'categorias/crear/',
        views.crear_categoria,
        name='crear_categoria'
    ),

    path(
        'categorias/editar/<int:categoria_id>/',
        views.editar_categoria,
        name='editar_categoria'
    ),

    path(
        'categorias/toggle/<int:categoria_id>/',
        views.toggle_categoria,
        name='toggle_categoria'
    ),

]