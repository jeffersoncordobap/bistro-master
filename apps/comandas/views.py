from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
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
    ).select_related('categoria').order_by('categoria__nombre', 'nombre')

    productos_por_categoria = {}
    for producto in productos:
        nombre_categoria = producto.categoria.nombre if producto.categoria else 'Sin categoria'
        productos_por_categoria.setdefault(nombre_categoria, []).append(producto)

    if request.method == 'POST':

        try:
            numero_mesa = int(request.POST.get('numero_mesa', 0))
            productos_ids = request.POST.getlist('productos')

            if not numero_mesa or numero_mesa < 1:
                messages.error(request, 'Debes ingresar un número de mesa válido.')
                return render(
                    request,
                    'comandas/registrar_comanda.html',
                    {
                        'productos': productos,
                        'productos_por_categoria': productos_por_categoria,
                    }
                )

            if not productos_ids:
                messages.error(request, 'Debes seleccionar al menos un producto.')
                return render(
                    request,
                    'comandas/registrar_comanda.html',
                    {
                        'productos': productos,
                        'productos_por_categoria': productos_por_categoria,
                    }
                )

            comanda = Comanda.objects.create(
                restaurante=request.user.restaurante,
                mesero=request.user,
                numero_mesa=numero_mesa,
                estado=Comanda.Estados.PENDIENTE
            )

            for producto_id in productos_ids:
                cantidad = int(request.POST.get(f'cantidad_{producto_id}', 1))
                nota = request.POST.get(f'nota_{producto_id}', '')
                ItemComanda.objects.create(
                    comanda=comanda,
                    producto_id=producto_id,
                    cantidad=cantidad,
                    nota=nota
                )

            messages.success(request, 'Pedido enviado correctamente.')
            return redirect('mis_comandas')
        
        except ValueError as e:
            messages.error(request, f'Error en los datos del formulario: {str(e)}')
            return render(
                request,
                'comandas/registrar_comanda.html',
                {
                    'productos': productos,
                    'productos_por_categoria': productos_por_categoria,
                }
            )
        except Exception as e:
            messages.error(request, f'Error al registrar la comanda: {str(e)}')
            return render(
                request,
                'comandas/registrar_comanda.html',
                {
                    'productos': productos,
                    'productos_por_categoria': productos_por_categoria,
                }
            )

    return render(
        request,
        'comandas/registrar_comanda.html',
        {
            'productos': productos,
            'productos_por_categoria': productos_por_categoria,
        }
    )


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def panel_pedidos(request):
    comandas = Comanda.objects.filter(
        restaurante=request.user.restaurante
    ).prefetch_related('items__producto').select_related('mesero').order_by('-fecha_creacion')

    return render(request, 'comandas/panel_pedidos.html', {'comandas': comandas})


# ── Endpoint JSON para polling (auto-refresco del panel) ──────────────────────
@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def api_panel_pedidos(request):
    """Devuelve las comandas activas (no entregadas) en JSON para polling."""
    ahora = timezone.now()
    comandas = Comanda.objects.filter(
        restaurante=request.user.restaurante
    ).prefetch_related('items__producto').select_related('mesero').order_by('-fecha_creacion')

    data = []
    for c in comandas:
        # Segundos transcurridos desde la creación
        segundos = int((ahora - c.fecha_creacion).total_seconds())
        items = [
            {
                'nombre': item.producto.nombre,
                'cantidad': item.cantidad,
                'nota': item.nota or '',
            }
            for item in c.items.all()
        ]
        data.append({
            'id': c.id,
            'mesa': c.numero_mesa,
            'estado': c.estado,
            'mesero': c.mesero.username,
            'segundos': segundos,
            'items': items,
        })

    return JsonResponse({'comandas': data})


# ── Cambiar estado (soporta AJAX y form normal) ───────────────────────────────
@login_required
@rol_requerido([Usuario.Roles.ADMIN])
@require_POST
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

    # Si la petición es AJAX devuelve JSON, si no redirige
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'estado': comanda.estado})

    return redirect('panel_pedidos')


@login_required
@rol_requerido([Usuario.Roles.MESERO])
def mis_comandas(request):
    # Calcular inicio y fin del día actual en UTC
    ahora = timezone.now()
    inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = inicio_dia + timedelta(days=1)

    comandas = Comanda.objects.filter(
        mesero=request.user,
        fecha_creacion__gte=inicio_dia,
        fecha_creacion__lt=fin_dia
    ).order_by('-fecha_creacion')

    return render(request, 'comandas/mis_comandas.html', {'comandas': comandas})


@login_required
@rol_requerido([Usuario.Roles.MESERO])
@require_POST
def marcar_comanda_entregada(request, comanda_id):
    """Permite al mesero marcar una comanda como entregada (solo si está en estado 'listo')"""
    comanda = get_object_or_404(
        Comanda,
        id=comanda_id,
        restaurante=request.user.restaurante,
        mesero=request.user
    )

    # Solo permitir marcar como entregado si está en estado 'listo'
    if comanda.estado != Comanda.Estados.LISTO:
        return JsonResponse({
            'ok': False,
            'error': 'Solo puedes marcar como entregado pedidos que estén en estado "Listo"'
        }, status=400)

    comanda.estado = Comanda.Estados.ENTREGADO
    comanda.save()

    return JsonResponse({'ok': True, 'estado': comanda.estado})