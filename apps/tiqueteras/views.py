from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import Usuario

from .models import Tiquetera
from .forms import TiqueteraForm


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def listar_tiqueteras(request):

    tiqueteras = Tiquetera.objects.filter(
        restaurante=request.user.restaurante
    ).select_related('plan').order_by('-creada')

    return render(
        request,
        'tiqueteras/listar_tiqueteras.html',
        {
            'tiqueteras': tiqueteras
        }
    )


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def crear_tiquetera(request):

    if request.method == 'POST':

        form = TiqueteraForm(
            request.POST,
            restaurante=request.user.restaurante
        )

        if form.is_valid():

            tiquetera = form.save(commit=False)

            tiquetera.restaurante = request.user.restaurante

            tiquetera.save()

            messages.success(
                request,
                'Tiquetera creada correctamente.'
            )

            return redirect('listar_tiqueteras')

    else:

        form = TiqueteraForm(
            restaurante=request.user.restaurante
        )

    return render(
        request,
        'tiqueteras/crear_tiquetera.html',
        {
            'form': form
        }
    )