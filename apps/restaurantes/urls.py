from django.urls import path

from . import views

urlpatterns = [
    path(
    'configuracion/',
    views.configuracion_restaurante,
    name='configuracion_restaurante'
    ),
]
