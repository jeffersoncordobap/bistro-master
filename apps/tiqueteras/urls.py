from django.urls import path
from . import views

urlpatterns = [

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

]