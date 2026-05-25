import json
import logging
from datetime import timedelta
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError
from django.db import transaction

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import Usuario
from apps.productos.models import Producto
from apps.restaurantes.models import Restaurante
from django.db.models import Q

from .models import PedidoDomicilio, ItemPedidoDomicilio
from .whatsapp import whatsapp_web_url

logger = logging.getLogger(__name__)


def checkout_domicilio(request, slug):

    restaurante = get_object_or_404(Restaurante, slug=slug)

    return render(
        request,
        'domicilios/checkout.html',
        {
            'restaurante': restaurante,
        }
    )


@require_POST
def crear_pedido_domicilio(request, slug):

    restaurante = get_object_or_404(Restaurante, slug=slug)

    if restaurante.estado != Restaurante.Estados.ABIERTO:
        return JsonResponse(
            {
                'ok': False,
                'error': 'El restaurante está cerrado en este momento.',
            },
            status=400,
        )

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse(
            {
                'ok': False,
                'error': 'JSON inválido.',
            },
            status=400,
        )

    cliente_nombre = (payload.get('cliente_nombre') or '').strip()
    cliente_telefono = (payload.get('cliente_telefono') or '').strip()
    direccion = (payload.get('direccion') or '').strip()
    referencia = (payload.get('referencia') or '').strip()

    items = payload.get('items') or []

    if not cliente_nombre or not cliente_telefono or not direccion:
        return JsonResponse(
            {
                'ok': False,
                'error': 'Nombre, teléfono y dirección son obligatorios.',
            },
            status=400,
        )

    if not isinstance(items, list) or not items:
        return JsonResponse(
            {
                'ok': False,
                'error': 'Debes seleccionar al menos un producto.',
            },
            status=400,
        )

    productos_ids = []
    normalized_items = []

    for it in items:
        try:
            producto_id = int(it.get('producto_id'))
            cantidad = int(it.get('cantidad', 1))
        except (TypeError, ValueError):
            return JsonResponse(
                {
                    'ok': False,
                    'error': 'Items inválidos.',
                },
                status=400,
            )

        if cantidad < 1:
            return JsonResponse(
                {
                    'ok': False,
                    'error': 'La cantidad debe ser mayor o igual a 1.',
                },
                status=400,
            )

        nota = (it.get('nota') or '').strip()

        productos_ids.append(producto_id)
        normalized_items.append(
            {
                'producto_id': producto_id,
                'cantidad': cantidad,
                'nota': nota,
            }
        )

    productos = Producto.objects.filter(
        id__in=productos_ids,
        restaurante=restaurante,
        disponible=True,
    )

    productos_map = {p.id: p for p in productos}

    if len(productos_map) != len(set(productos_ids)):
        return JsonResponse(
            {
                'ok': False,
                'error': 'Uno o más productos no están disponibles.',
            },
            status=400,
        )

    try:
        pedido = PedidoDomicilio.objects.create(
            restaurante=restaurante,
            estado=PedidoDomicilio.Estados.PENDIENTE,
            cliente_nombre=cliente_nombre,
            cliente_telefono=cliente_telefono,
            direccion=direccion,
            referencia=referencia,
            total=Decimal('0.00'),
        )
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {
                'ok': False,
                'error': (
                    'El sistema no está listo: faltan migraciones de domicilios. '
                    'Ejecuta: python manage.py migrate'
                ),
            },
            status=500,
        )

    total = Decimal('0.00')

    for it in normalized_items:
        producto = productos_map[it['producto_id']]
        cantidad = it['cantidad']

        try:
            ItemPedidoDomicilio.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                nota=it['nota'],
            )
        except (OperationalError, ProgrammingError):
            return JsonResponse(
                {
                    'ok': False,
                    'error': (
                        'El sistema no está listo: faltan migraciones de domicilios. '
                        'Ejecuta: python manage.py migrate'
                    ),
                },
                status=500,
            )

        total += (producto.precio or Decimal('0.00')) * Decimal(cantidad)

    pedido.total = total
    pedido.save(update_fields=['total'])

    return JsonResponse(
        {
            'ok': True,
            'pedido_id': pedido.id,
            'fecha_creacion': timezone.localtime(pedido.fecha_creacion).isoformat(),
        }
    )


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
@require_POST
def cambiar_estado_pedido_domicilio(request, pedido_id):

    try:
        pedido = get_object_or_404(
            PedidoDomicilio,
            id=pedido_id,
            restaurante=request.user.restaurante,
        )
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {
                'ok': False,
                'error': (
                    'El sistema no está listo: faltan migraciones de domicilios. '
                    'Ejecuta: python manage.py migrate'
                ),
            },
            status=500,
        )

    nuevo_estado = request.POST.get('estado')

    if nuevo_estado in dict(PedidoDomicilio.Estados.choices):
        pedido.estado = nuevo_estado
        update_fields = ['estado']

        # Nuevo flujo:
        # - ADMIN marca el pedido como "entregado" (listo para que un domiciliario lo tome).
        # - En este punto NO debe existir estado_entrega; se asigna cuando el domiciliario marca "Recibido".
        if nuevo_estado == PedidoDomicilio.Estados.ENTREGADO:
            pedido.estado_entrega = None
            pedido.fecha_recibido = None
            pedido.fecha_en_camino = None
            pedido.fecha_entregado = None
            update_fields.extend(
                ['estado_entrega', 'fecha_recibido', 'fecha_en_camino', 'fecha_entregado']
            )

        pedido.save(update_fields=update_fields)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'ok': True,
                'estado': pedido.estado,
            }
        )

    return JsonResponse({'ok': True})


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def panel_domicilios(request):

    ahora = timezone.now()
    inicio_dia = timezone.localtime(ahora).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    fin_dia = inicio_dia + timedelta(days=1)

    pedidos = PedidoDomicilio.objects.filter(
        restaurante=request.user.restaurante,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        estado_entrega__isnull=False,
        fecha_creacion__gte=inicio_dia,
        fecha_creacion__lt=fin_dia,
    ).prefetch_related(
        'items__producto'
    ).select_related(
        'domiciliario'
    ).order_by(
        '-fecha_creacion'
    )

    domiciliarios = Usuario.objects.filter(
        restaurante=request.user.restaurante,
        rol=Usuario.Roles.DOMICILIARIO,
        is_active=True,
    ).order_by('username')

    stats = {
        'recibido': pedidos.filter(estado_entrega=PedidoDomicilio.EstadosEntrega.RECIBIDO).count(),
        'en_camino': pedidos.filter(estado_entrega=PedidoDomicilio.EstadosEntrega.EN_CAMINO).count(),
        'entregado': pedidos.filter(estado_entrega=PedidoDomicilio.EstadosEntrega.ENTREGADO).count(),
    }

    return render(
        request,
        'domicilios/panel_domicilios.html',
        {
            'pedidos': pedidos,
            'domiciliarios': domiciliarios,
            'stats': stats,
        }
    )


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
@require_POST
def eliminar_pedido_domicilio(request, pedido_id):

    pedido = get_object_or_404(
        PedidoDomicilio,
        id=pedido_id,
        restaurante=request.user.restaurante,
    )

    pedido.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    return redirect('panel_pedidos')


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def historial_domicilios(request):

    try:
        pedidos = (
            PedidoDomicilio.objects.filter(
                restaurante=request.user.restaurante
            )
            .prefetch_related('items__producto')
            .select_related('domiciliario')
            .order_by('-fecha_creacion')
        )
    except (OperationalError, ProgrammingError):
        pedidos = []

    return render(
        request,
        'domicilios/historial_domicilios.html',
        {
            'pedidos': pedidos,
        }
    )


@login_required
@rol_requerido([Usuario.Roles.DOMICILIARIO])
def domiciliario_domicilios(request):

    pedidos = (
        PedidoDomicilio.objects.filter(
            restaurante=request.user.restaurante,
            estado=PedidoDomicilio.Estados.ENTREGADO,
        )
        .filter(
            Q(domiciliario__isnull=True)
            | Q(domiciliario=request.user, estado_entrega__isnull=True)
        )
        .prefetch_related('items__producto')
        .order_by('-fecha_creacion')
    )

    return render(
        request,
        'domicilios/domiciliario_domicilios.html',
        {
            'pedidos': pedidos,
        }
    )


@login_required
@rol_requerido([Usuario.Roles.DOMICILIARIO])
@require_POST
def domiciliario_marcar_recibido(request, pedido_id):

    now = timezone.now()

    with transaction.atomic():
        pedido = get_object_or_404(
            PedidoDomicilio.objects.select_for_update(),
            id=pedido_id,
            restaurante=request.user.restaurante,
            estado=PedidoDomicilio.Estados.ENTREGADO,
        )

        # Si ya tiene estado_entrega y ya existe domiciliario, está tomado.
        if pedido.estado_entrega and pedido.domiciliario_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Este domicilio ya fue tomado.'}, status=409)
            messages.error(request, 'Este domicilio ya fue tomado por otro domiciliario.')
            return redirect('domiciliario_domicilios')

        # Compatibilidad con pedidos antiguos: pudieron quedar con estado_entrega="recibido"
        # pero sin domiciliario asignado. En ese caso permitimos que el domiciliario lo tome.
        if pedido.estado_entrega and not pedido.domiciliario_id:
            if pedido.estado_entrega != PedidoDomicilio.EstadosEntrega.RECIBIDO:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'ok': False, 'error': 'Este domicilio no está disponible.'}, status=409)
                messages.error(request, 'Este domicilio no está disponible.')
                return redirect('domiciliario_domicilios')

        if pedido.domiciliario and pedido.domiciliario_id != request.user.id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Este domicilio ya está asignado a otro domiciliario.'}, status=403)
            messages.error(request, 'Este domicilio ya está asignado a otro domiciliario.')
            return redirect('domiciliario_domicilios')

        pedido.domiciliario = request.user
        pedido.estado_entrega = PedidoDomicilio.EstadosEntrega.RECIBIDO
        pedido.fecha_recibido = pedido.fecha_recibido or now
        pedido.save(update_fields=['domiciliario', 'estado_entrega', 'fecha_recibido'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    return redirect('domiciliario_mis_domicilios')


@login_required
@rol_requerido([Usuario.Roles.DOMICILIARIO])
def domiciliario_mis_domicilios(request):

    pedidos = (
        PedidoDomicilio.objects.filter(
            restaurante=request.user.restaurante,
            estado=PedidoDomicilio.Estados.ENTREGADO,
            domiciliario=request.user,
            estado_entrega__in=[
                PedidoDomicilio.EstadosEntrega.RECIBIDO,
                PedidoDomicilio.EstadosEntrega.EN_CAMINO,
                PedidoDomicilio.EstadosEntrega.ENTREGADO,
            ],
        )
        .prefetch_related('items__producto')
        .order_by('-fecha_creacion')
    )

    return render(
        request,
        'domicilios/domiciliario_mis_domicilios.html',
        {
            'pedidos': pedidos,
        }
    )


@login_required
@rol_requerido([Usuario.Roles.DOMICILIARIO])
def domiciliario_historial_domicilios(request):

    pedidos = (
        PedidoDomicilio.objects.filter(
            restaurante=request.user.restaurante,
            estado=PedidoDomicilio.Estados.ENTREGADO,
            domiciliario=request.user,
            estado_entrega__in=[
                PedidoDomicilio.EstadosEntrega.RECIBIDO,
                PedidoDomicilio.EstadosEntrega.EN_CAMINO,
                PedidoDomicilio.EstadosEntrega.ENTREGADO,
            ],
        )
        .prefetch_related('items__producto')
        .order_by('-fecha_creacion')
    )

    return render(
        request,
        'domicilios/domiciliario_historial_domicilios.html',
        {
            'pedidos': pedidos,
        }
    )


@login_required
@rol_requerido([Usuario.Roles.DOMICILIARIO])
@require_POST
def domiciliario_marcar_en_camino(request, pedido_id):

    pedido = get_object_or_404(
        PedidoDomicilio,
        id=pedido_id,
        restaurante=request.user.restaurante,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        domiciliario=request.user,
    )

    if pedido.estado_entrega not in [PedidoDomicilio.EstadosEntrega.RECIBIDO, PedidoDomicilio.EstadosEntrega.EN_CAMINO]:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False}, status=400)
        messages.error(request, 'No se puede marcar “En camino” en el estado actual.')
        return redirect('domiciliario_mis_domicilios')

    if pedido.estado_entrega != PedidoDomicilio.EstadosEntrega.EN_CAMINO:
        pedido.estado_entrega = PedidoDomicilio.EstadosEntrega.EN_CAMINO
        pedido.fecha_en_camino = pedido.fecha_en_camino or timezone.now()
        pedido.save(update_fields=['estado_entrega', 'fecha_en_camino'])

    items_lines = []
    for it in pedido.items.select_related('producto').all():
        line = f"• {it.cantidad}x {it.producto.nombre}"
        if it.nota:
            line += f" ({it.nota})"
        items_lines.append(line)
    items_texto = "\n".join(items_lines).strip() or "• (Sin items)"

    text = (
        f"🍔 *Pedido confirmado*\n\n"
        f"Hola {pedido.cliente_nombre} 👋\n\n"
        f"Tu pedido en *{pedido.restaurante.nombre}* "
        f"ha sido confirmado y ya está en camino🧑‍🍳\n\n"
        f"📦 *Tu pedido:*\n\n"
        f"{items_texto}\n"
        f"💰 Total: ${pedido.total}\n"
        f"🕒 Tiempo estimado: 20 minutos\n"
        f"🏍️ Estado: En camino\n\n"
        f"¡Gracias por tu pedido! 🚀"
    )
    url = whatsapp_web_url(to_phone=pedido.cliente_telefono, text=text)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'whatsapp_url': url})

    return redirect(url)


@login_required
@rol_requerido([Usuario.Roles.DOMICILIARIO])
@require_POST
def domiciliario_marcar_entregado(request, pedido_id):

    pedido = get_object_or_404(
        PedidoDomicilio,
        id=pedido_id,
        restaurante=request.user.restaurante,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        domiciliario=request.user,
    )

    if pedido.estado_entrega not in [
        PedidoDomicilio.EstadosEntrega.RECIBIDO,
        PedidoDomicilio.EstadosEntrega.EN_CAMINO,
        PedidoDomicilio.EstadosEntrega.ENTREGADO,
    ]:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False}, status=400)
        messages.error(request, 'No se puede marcar “Entregado” en el estado actual.')
        return redirect('domiciliario_mis_domicilios')

    if pedido.estado_entrega != PedidoDomicilio.EstadosEntrega.ENTREGADO:
        pedido.estado_entrega = PedidoDomicilio.EstadosEntrega.ENTREGADO
        pedido.fecha_entregado = pedido.fecha_entregado or timezone.now()
        pedido.save(update_fields=['estado_entrega', 'fecha_entregado'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    return redirect('domiciliario_mis_domicilios')


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
@require_POST
def asignar_domiciliario(request, pedido_id):

    pedido = get_object_or_404(
        PedidoDomicilio,
        id=pedido_id,
        restaurante=request.user.restaurante,
    )

    domiciliario_id = request.POST.get('domiciliario_id')

    if domiciliario_id:
        domiciliario = get_object_or_404(
            Usuario,
            id=domiciliario_id,
            restaurante=request.user.restaurante,
            rol=Usuario.Roles.DOMICILIARIO,
        )
        pedido.domiciliario = domiciliario
        pedido.save(update_fields=['domiciliario'])
    else:
        pedido.domiciliario = None
        pedido.save(update_fields=['domiciliario'])

    return JsonResponse({'ok': True})


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
@require_POST
def cambiar_estado_entrega_domicilio(request, pedido_id):

    pedido = get_object_or_404(
        PedidoDomicilio,
        id=pedido_id,
        restaurante=request.user.restaurante,
    )

    estado = request.POST.get('estado_entrega')

    if estado not in dict(PedidoDomicilio.EstadosEntrega.choices):
        return JsonResponse({'ok': False}, status=400)

    update_fields = ['estado_entrega']
    now = timezone.now()

    if estado == PedidoDomicilio.EstadosEntrega.RECIBIDO:
        pedido.fecha_recibido = pedido.fecha_recibido or now
        update_fields.append('fecha_recibido')
    elif estado == PedidoDomicilio.EstadosEntrega.EN_CAMINO:
        pedido.fecha_en_camino = pedido.fecha_en_camino or now
        update_fields.append('fecha_en_camino')
    elif estado == PedidoDomicilio.EstadosEntrega.ENTREGADO:
        pedido.fecha_entregado = pedido.fecha_entregado or now
        update_fields.append('fecha_entregado')

    pedido.estado_entrega = estado
    pedido.save(update_fields=update_fields)

    return JsonResponse({'ok': True})
