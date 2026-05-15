from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.restaurantes.forms import RestauranteForm
from apps.usuarios.forms import RegistroAdministradorForm
from .forms import LoginForm

from .decorators import rol_requerido
from apps.usuarios.models import Usuario


def registro_restaurante(request):

    if request.method == 'POST':
        
        restaurante_form = RestauranteForm(
            request.POST,
            prefix='restaurante'
        )

        usuario_form = RegistroAdministradorForm(
            request.POST,
            prefix='usuario'
        )

        if restaurante_form.is_valid() and usuario_form.is_valid():

            restaurante = restaurante_form.save()

            usuario = usuario_form.save(commit=False)

            usuario.restaurante = restaurante
            usuario.rol = Usuario.Roles.ADMIN

            usuario.set_password(
                usuario_form.cleaned_data['password1']
            )

            usuario.save()

            messages.success(
                request,
                'Restaurante creado correctamente.'
            )

            return redirect('inicio')
        

    else:

        restaurante_form = RestauranteForm(prefix='restaurante')

        usuario_form = RegistroAdministradorForm(prefix='usuario')

    context = {
        'restaurante_form': restaurante_form,
        'usuario_form': usuario_form
    }

    return render(request, 'usuarios/registro.html', context)

def login_usuario(request):

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            usuario = authenticate(
                request,
                username=username,
                password=password
            )

            if usuario is not None:

                login(request, usuario)

                if usuario.rol == Usuario.Roles.ADMIN:

                    return redirect('panel_admin')

                elif usuario.rol == Usuario.Roles.MESERO:

                    return redirect('panel_mesero')

                elif usuario.rol == Usuario.Roles.DOMICILIARIO:

                    return redirect('panel_domiciliario')

                else:

                    return redirect('inicio')

            else:

                messages.error(
                    request,
                    'Usuario o contraseña incorrectos.'
                )

    else:

        form = LoginForm()

    context = {
        'form': form
    }

    return render(
        request,
        'usuarios/login.html',
        context
    )
    
@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def panel_admin(request):

    return render(
        request,
        'usuarios/panel_admin.html'
    )


@login_required
@rol_requerido([Usuario.Roles.MESERO])
def panel_mesero(request):

    return render(
        request,
        'usuarios/panel_mesero.html'
    )


@login_required
@rol_requerido([Usuario.Roles.DOMICILIARIO])
def panel_domiciliario(request):

    return render(
        request,
        'usuarios/panel_domiciliario.html'
    )