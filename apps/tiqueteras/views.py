from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import Usuario

from .models import Tiquetera, PlanTiquetera
from .forms import TiqueteraForm, PlanTiqueteraForm


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
            tiquetera.activa = True
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
    
@login_required
@rol_requerido([Usuario.Roles.ADMIN])    
def listar_planes(request):

    restaurante = request.user.restaurante

    planes = PlanTiquetera.objects.filter(
        restaurante=restaurante
    ).order_by('-id')

    return render(
        request,
        'tiqueteras/listar_planes.html',
        {
            'planes': planes
        }
    )
    
@login_required
@rol_requerido([Usuario.Roles.ADMIN])   
def crear_plan(request):

    restaurante = request.user.restaurante

    if request.method == 'POST':

        form = PlanTiqueteraForm(request.POST)

        if form.is_valid():

            plan = form.save(commit=False)

            plan.restaurante = restaurante

            plan.save()

            messages.success(
                request,
                'Plan creado correctamente.'
            )

            return redirect('listar_planes')

    else:

        form = PlanTiqueteraForm()

    return render(
        request,
        'tiqueteras/crear_plan.html',
        {
            'form': form
        }
    )
    
    
    
@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def editar_plan(request, plan_id):

    restaurante = request.user.restaurante

    plan = get_object_or_404(
        PlanTiquetera,
        id=plan_id,
        restaurante=restaurante
    )

    if request.method == 'POST':

        form = PlanTiqueteraForm(
            request.POST,
            instance=plan
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Plan actualizado correctamente.'
            )

            return redirect('listar_planes')

    else:

        form = PlanTiqueteraForm(instance=plan)

    return render(
        request,
        'tiqueteras/editar_plan.html',
        {
            'form': form,
            'plan': plan
        }
    )
    
    
@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def cambiar_estado_plan(request, plan_id):

    restaurante = request.user.restaurante

    plan = get_object_or_404(
        PlanTiquetera,
        id=plan_id,
        restaurante=restaurante
    )

    plan.activo = not plan.activo

    plan.save()

    estado = 'activado' if plan.activo else 'desactivado'

    messages.success(
        request,
        f'Plan {estado} correctamente.'
    )

    return redirect('listar_planes')


