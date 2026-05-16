from django.shortcuts import redirect, render, get_object_or_404

from apps.usuarios.models import Usuario
from apps.restaurantes.models import Restaurante

from .forms import RestauranteUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.usuarios.decorators import rol_requerido

# Create your views here.
@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def configuracion_restaurante(request):

    restaurante = request.user.restaurante

    if request.method == 'POST':

        form = RestauranteUpdateForm(
            request.POST,
            instance=restaurante
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Configuración actualizada correctamente.'
            )

            return redirect('configuracion_restaurante')

    else:

        form = RestauranteUpdateForm(
            instance=restaurante
        )

    context = {
        'form': form,
        'restaurante': restaurante
    }

    return render(
        request,
        'dashboard/configuracion/configuracion.html',
        context
    )
    

def pagina_restaurante(request, slug):

    restaurante = get_object_or_404(
        Restaurante,
        slug=slug
    )

    context = {
        'restaurante': restaurante
    }

    return render(
        request,
        'restaurantes/pagina_restaurante.html',
        context
    )
