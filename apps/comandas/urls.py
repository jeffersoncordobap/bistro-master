from django.urls import path
from . import views

urlpatterns = [
    path(
        'comanda/registrar/',
        views.registrar_comanda,
        name='registrar_comanda'
    ),
    path(
        'panel-pedidos/',
        views.panel_pedidos,
        name='panel_pedidos'
    ),
    path(
        'panel-pedidos/historial/',
        views.historial_pedidos,
        name='historial_pedidos'
    ),
    path(
        'comanda/<int:comanda_id>/estado/',
        views.cambiar_estado_comanda,
        name='cambiar_estado_comanda'
    ),
    path(
        'comanda/<int:comanda_id>/eliminar/',
        views.eliminar_comanda,
        name='eliminar_comanda',
    ),
    # Endpoint JSON para polling en tiempo real
    path(
        'api/panel-pedidos/',
        views.api_panel_pedidos,
        name='api_panel_pedidos'
    ),
    path(
        'mis-comandas/',
        views.mis_comandas,
        name='mis_comandas'
    ),
    # Endpoint para que el mesero marque como entregado
    path(
        'comanda/<int:comanda_id>/marcar-entregado/',
        views.marcar_comanda_entregada,
        name='marcar_comanda_entregada'
    ),
]
