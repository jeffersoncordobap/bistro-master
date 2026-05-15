from django.shortcuts import render, redirect

from apps.restaurantes.forms import RestauranteForm
from apps.usuarios.forms import RegistroAdministradorForm
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

            return redirect('inicio')

    else:

        restaurante_form = RestauranteForm(prefix='restaurante')

        usuario_form = RegistroAdministradorForm(prefix='usuario')

    context = {
        'restaurante_form': restaurante_form,
        'usuario_form': usuario_form
    }

    return render(request, 'usuarios/registro.html', context)
