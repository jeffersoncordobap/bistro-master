from django.urls import path

from . import views


urlpatterns = [
    path(
        'registro/',
        views.registro_restaurante,
        name='registro'
    ),
    
    path(
    'login/',
    views.login_usuario,
    name='login'
    ),
    
    path(
    'panel-admin/',
    views.panel_admin,
    name='panel_admin'
    ),

    path(
        'panel-mesero/',
        views.panel_mesero,
        name='panel_mesero'
    ),

    path(
        'panel-domiciliario/',
        views.panel_domiciliario,
        name='panel_domiciliario'
    ),
]