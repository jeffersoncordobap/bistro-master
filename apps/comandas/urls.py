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
        'comanda/<int:comanda_id>/estado/',
        views.cambiar_estado_comanda,
        name='cambiar_estado_comanda'
    ),
    path(
        'mis-comandas/',
        views.mis_comandas,
        name='mis_comandas'
    ),
]