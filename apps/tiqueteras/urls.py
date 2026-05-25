from django.urls import path
from . import views

urlpatterns = [

    path(
        'historial/',
        views.historial_tiqueteras,
        name='historial_tiqueteras'
    ),
    path(
        'buscar/',
        views.buscar_tiquetera,
        name='buscar_tiquetera'
    ),

    path(
        '',
        views.listar_tiqueteras,
        name='listar_tiqueteras'
    ),

    path(
        'crear/',
        views.crear_tiquetera,
        name='crear_tiquetera'
    ),

    path(
    'planes/',
    views.listar_planes,
    name='listar_planes'
    ),

    path(
        'planes/crear/',
        views.crear_plan,
        name='crear_plan'
    ),

    path(
        'planes/<int:plan_id>/editar/',
        views.editar_plan,
        name='editar_plan'
    ),

    path(
        'planes/<int:plan_id>/estado/',
        views.cambiar_estado_plan,
        name='cambiar_estado_plan'
    ),
]