from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import Usuario
from apps.productos.models import Producto
from .models import Comanda, ItemComanda


@login_required
@rol_requerido([Usuario.Roles.MESERO])
def registrar_comanda(request):

    productos = Producto.objects.filter(
        restaurante=request.user.restaurante,
        disponible=True
    )

    if request.method == 'POST':

        numero_mesa = request.POST.get('numero_mesa')
        productos_ids = request.POST.getlist('productos')
        cantidades = request.POST.getlist('cantidades')
        notas = request.POST.getlist('notas')

        if not productos_ids:
            messages.error(request, 'Debes seleccionar al menos un producto.')
            return render(request, 'comandas/registrar_comanda.html', {'productos': productos})

        comanda = Comanda.objects.create(
            restaurante=request.user.restaurante,
            mesero=request.user,
            numero_mesa=numero_mesa,
            estado=Comanda.Estados.PENDIENTE
        )

        for i, producto_id in enumerate(productos_ids):
            ItemComanda.objects.create(
                comanda=comanda,
                producto_id=producto_id,
                cantidad=cantidades[i] if i < len(cantidades) else 1,
                nota=notas[i] if i < len(notas) else ''
            )

        messages.success(request, 'Pedido enviado correctamente.')
        return redirect('registrar_comanda')

    return render(request, 'comandas/registrar_comanda.html', {'productos': productos})


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def panel_pedidos(request):

    comandas = Comanda.objects.filter(
        restaurante=request.user.restaurante
    ).order_by('-fecha_creacion')

    return render(request, 'comandas/panel_pedidos.html', {'comandas': comandas})


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def cambiar_estado_comanda(request, comanda_id):

    comanda = get_object_or_404(
        Comanda,
        id=comanda_id,
        restaurante=request.user.restaurante
    )

    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Comanda.Estados.choices):
        comanda.estado = nuevo_estado
        comanda.save()

    return redirect('panel_pedidos')


@login_required
@rol_requerido([Usuario.Roles.MESERO])
def mis_comandas(request):
    from django.utils import timezone
    hoy = timezone.now().date()
    comandas = Comanda.objects.filter(
        mesero=request.user,
        fecha_creacion__date=hoy
    ).order_by('-fecha_creacion')

    return render(request, 'comandas/mis_comandas.html', {'comandas': comandas})