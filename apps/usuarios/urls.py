from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm

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
    
    path(
    'usuarios/',
    views.lista_usuarios,
    name='lista_usuarios'
    ),
    
    path(
    'usuarios/crear/',
    views.crear_usuario,
    name='crear_usuario'
    ),
    
    path(
    'usuarios/<int:usuario_id>/editar/',
    views.editar_usuario,
    name='editar_usuario'
    ),
    
    path(
    'usuarios/<int:usuario_id>/toggle/',
    views.toggle_usuario,
    name='toggle_usuario'
    ),
    
    path(
    'logout/',
    views.logout_usuario,
    name='logout'
    ),
    
    
    
    path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset.html',
        form_class=CustomPasswordResetForm
    ),
    name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]