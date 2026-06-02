from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import Usuario

from apps.productos.models import Producto

from apps.tiqueteras.models import (
    Tiquetera,
    ConsumoTiquetera
)

from apps.domicilios.models import PedidoDomicilio

from .models import (
    Comanda,
    ItemComanda,
    TipoConsumo
)


@login_required
@rol_requerido([Usuario.Roles.MESERO])
def registrar_comanda(request):

    productos = Producto.objects.filter(
        restaurante=request.user.restaurante,
        disponible=True
    ).select_related(
        'categoria'
    ).order_by(
        'categoria__nombre',
        'nombre'
    )

    productos_por_categoria = {}

    for producto in productos:

        nombre_categoria = (
            producto.categoria.nombre
            if producto.categoria
            else 'Sin categoria'
        )

        productos_por_categoria.setdefault(
            nombre_categoria,
            []
        ).append(producto)

    tiqueteras = Tiquetera.objects.filter(
        restaurante=request.user.restaurante,
        activa=True,
        saldo_consumos__gt=0
    )

    context = {

        'productos': productos,

        'productos_por_categoria': productos_por_categoria,

        'tiqueteras': tiqueteras,
        
        'restaurante_cerrado': (
        request.user.restaurante.estado ==
        request.user.restaurante.Estados.CERRADO
    )
    }

    if request.method == 'POST':
        restaurante = request.user.restaurante
        if restaurante.estado == restaurante.Estados.CERRADO:
            messages.error(
                request,
                'No puedes registrar pedidos porque el restaurante está cerrado.'
            )
            return render(
                request,
                'comandas/registrar_comanda.html',
                context
            )

        try:

            numero_mesa = int(
                request.POST.get('numero_mesa', 0)
            )

            productos_ids = request.POST.getlist(
                'productos'
            )

            tipo_consumo = request.POST.get(
                'tipo_consumo',
                TipoConsumo.NORMAL
            )

            tiquetera_id = request.POST.get(
                'tiquetera'
            )
            if numero_mesa < 1:

                messages.error(
                    request,
                    'Debes ingresar un número de mesa válido.'
                )

                return render(
                    request,
                    'comandas/registrar_comanda.html',
                    context
                )

            if not productos_ids:

                messages.error(
                    request,
                    'Debes seleccionar al menos un producto.'
                )

                return render(
                    request,
                    'comandas/registrar_comanda.html',
                    context
                )

            tiquetera = None

            if tipo_consumo == TipoConsumo.TIQUETERA:

                if not tiquetera_id:

                    messages.error(
                        request,
                        'Debes seleccionar una tiquetera.'
                    )

                    return render(
                        request,
                        'comandas/registrar_comanda.html',
                        context
                    )

                try:

                    tiquetera = Tiquetera.objects.get(
                        id=tiquetera_id,
                        restaurante=request.user.restaurante
                    )

                except Tiquetera.DoesNotExist:

                    messages.error(
                        request,
                        'La tiquetera seleccionada no existe.'
                    )

                    return render(
                        request,
                        'comandas/registrar_comanda.html',
                        context
                    )

                if not tiquetera.esta_vigente:

                    messages.error(
                        request,
                        'La tiquetera no tiene saldo o está vencida.'
                    )

                    return render(
                        request,
                        'comandas/registrar_comanda.html',
                        context
                    )
            with transaction.atomic():
                comanda = Comanda.objects.create(

                    restaurante=request.user.restaurante,

                    mesero=request.user,

                    numero_mesa=numero_mesa,

                    estado=Comanda.Estados.PENDIENTE,

                    tipo_consumo=tipo_consumo,

                    tiquetera=tiquetera
                )

                for producto_id in productos_ids:
                    if tiquetera and not tiquetera.plan.permite_multiples_consumos:
                        cantidad = 1
                        
                    else:
                        cantidad = int(
                            request.POST.get(
                                f'cantidad_{producto_id}',
                                1
                            )
                        )

                    nota = request.POST.get(
                        f'nota_{producto_id}',
                        ''
                    )
                    
                    producto = Producto.objects.get(id=producto_id,restaurante=request.user.restaurante)
                    if producto.control_stock:
                        producto.descontar_stock(cantidad)

                    ItemComanda.objects.create(

                        comanda=comanda,

                        producto_id=producto_id,

                        cantidad=cantidad,

                        nota=nota
                    )

                if tiquetera:
                    #Agregue apartado para multiples consumos de tiquetera en una misma comanda, se suman las cantidades de cada producto seleccionado
                    if tiquetera.plan.permite_multiples_consumos:
                        cantidad_consumos = sum(

                            int(request.POST.get(
                                f'cantidad_{pid}',
                                1
                            )) for pid in productos_ids
                        )
                        tiquetera.consumir(cantidad_consumos)
                    else:
                        tiquetera.consumir()

                    if tiquetera.saldo_consumos <= 0:

                        tiquetera.activa = False

                    tiquetera.save()

                    ConsumoTiquetera.objects.create(

                        tiquetera=tiquetera,

                        comanda=comanda,

                        cantidad=cantidad_consumos if tiquetera.plan.permite_multiples_consumos else 1,

                        registrado_por=request.user
                    )

            messages.success(
                request,
                'Pedido enviado correctamente.'
            )

            return redirect('mis_comandas')

        except ValueError as e:
            messages.error(
                request,
                f'Error en los datos del formulario: {str(e)}'
            )

            return render(
                request,
                'comandas/registrar_comanda.html',
                context
            )

        except Exception as e:
            raise e

    return render(
        request,
        'comandas/registrar_comanda.html',
        context
    )


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def panel_pedidos(request):

    comandas = Comanda.objects.filter(
        restaurante=request.user.restaurante
    ).prefetch_related(
        'items__producto'
    ).select_related(
        'mesero',
        'tiquetera'
    ).order_by(
        '-fecha_creacion'
    )

    return render(
        request,
        'comandas/panel_pedidos.html',
        {
            'comandas': comandas
        }
    )


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def historial_pedidos(request):

    comandas = Comanda.objects.filter(
        restaurante=request.user.restaurante
    ).prefetch_related(
        'items__producto'
    ).select_related(
        'mesero',
        'tiquetera'
    )

    try:
        pedidos_domicilio = list(
            PedidoDomicilio.objects.filter(
                restaurante=request.user.restaurante
            ).prefetch_related(
                'items__producto'
            )
        )
    except (OperationalError, ProgrammingError):
        pedidos_domicilio = []

    rows = []

    for c in comandas:

        rows.append(
            {
                'tipo': 'comanda',
                'fecha': c.fecha_creacion,
                'estado': c.estado,
                'mesa': c.numero_mesa,
                'mesero': c.mesero.username,
                'tipo_consumo': c.tipo_consumo,
                'tiquetera_cliente': (
                    c.tiquetera.cliente_nombre
                    if c.tiquetera
                    else None
                ),
                'items': c.items.all(),
                'total': None,
                'cliente_nombre': None,
                'cliente_telefono': None,
                'direccion': None,
                'referencia': None,
            }
        )

    for p in pedidos_domicilio:

        rows.append(
            {
                'tipo': 'domicilio',
                'fecha': p.fecha_creacion,
                'estado': p.estado,
                'mesa': None,
                'mesero': None,
                'tipo_consumo': None,
                'tiquetera_cliente': None,
                'items': p.items.all(),
                'total': p.total,
                'cliente_nombre': p.cliente_nombre,
                'cliente_telefono': p.cliente_telefono,
                'direccion': p.direccion,
                'referencia': p.referencia,
            }
        )

    rows.sort(key=lambda r: r['fecha'], reverse=True)

    return render(
        request,
        'comandas/historial_pedidos.html',
        {
            'rows': rows,
        }
    )


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
def api_panel_pedidos(request):

    ahora = timezone.now()

    comandas = Comanda.objects.filter(
        restaurante=request.user.restaurante
    ).prefetch_related(
        'items__producto'
    ).select_related(
        'mesero',
        'tiquetera'
    ).order_by(
        '-fecha_creacion'
    )

    try:
        pedidos_domicilio = list(
            PedidoDomicilio.objects.filter(
                restaurante=request.user.restaurante
            ).prefetch_related(
                'items__producto'
            ).order_by(
                '-fecha_creacion'
            )
        )
    except (OperationalError, ProgrammingError):
        pedidos_domicilio = []

    data = []

    for c in comandas:

        segundos = int(
            (ahora - c.fecha_creacion).total_seconds()
        )

        items = [

            {
                'nombre': item.producto.nombre,
                'cantidad': item.cantidad,
                'nota': item.nota or '',
            }

            for item in c.items.all()
        ]

        data.append({

            'tipo': 'comanda',
            'id': c.id,
            'uid': f'comanda-{c.id}',

            'mesa': c.numero_mesa,

            'estado': c.estado,

            'mesero': c.mesero.username,

            'segundos': segundos,

            'created_ts': int(c.fecha_creacion.timestamp()),

            'tipo_consumo': c.tipo_consumo,

            'tiquetera_cliente': (
                c.tiquetera.cliente_nombre
                if c.tiquetera
                else None
            ),

            'items': items,
        })

    for p in pedidos_domicilio:

        segundos = int(
            (ahora - p.fecha_creacion).total_seconds()
        )

        items = [
            {
                'nombre': item.producto.nombre,
                'cantidad': item.cantidad,
                'nota': item.nota or '',
            }
            for item in p.items.all()
        ]

        data.append({
            'tipo': 'domicilio',
            'id': p.id,
            'uid': f'domicilio-{p.id}',
            'mesa': None,
            'estado': p.estado,
            'mesero': None,
            'segundos': segundos,
            'created_ts': int(p.fecha_creacion.timestamp()),
            'tipo_consumo': None,
            'tiquetera_cliente': None,
            'cliente_nombre': p.cliente_nombre,
            'cliente_telefono': p.cliente_telefono,
            'direccion': p.direccion,
            'referencia': p.referencia,
            'items': items,
        })

    data.sort(key=lambda x: x.get('created_ts', 0), reverse=True)

    return JsonResponse({
        'comandas': data
    })


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

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        return JsonResponse({
            'ok': True,
            'estado': comanda.estado
        })

    return redirect('panel_pedidos')


@login_required
@rol_requerido([Usuario.Roles.ADMIN])
@require_POST
def eliminar_comanda(request, comanda_id):

    comanda = get_object_or_404(
        Comanda,
        id=comanda_id,
        restaurante=request.user.restaurante,
    )

    comanda.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    messages.success(request, 'Pedido eliminado correctamente.')
    return redirect('panel_pedidos')


@login_required
@rol_requerido([Usuario.Roles.MESERO])
def mis_comandas(request):

    ahora = timezone.now()

    inicio_dia = ahora.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    fin_dia = inicio_dia + timedelta(days=1)

    comandas = Comanda.objects.filter(

        mesero=request.user,

        fecha_creacion__gte=inicio_dia,

        fecha_creacion__lt=fin_dia

    ).order_by(
        '-fecha_creacion'
    )

    return render(
        request,
        'comandas/mis_comandas.html',
        {
            'comandas': comandas
        }
    )


@login_required
@rol_requerido([Usuario.Roles.MESERO])
@require_POST
def marcar_comanda_entregada(request, comanda_id):

    comanda = get_object_or_404(

        Comanda,

        id=comanda_id,

        restaurante=request.user.restaurante,

        mesero=request.user
    )

    if comanda.estado != Comanda.Estados.LISTO:

        return JsonResponse({

            'ok': False,

            'error': (
                'Solo puedes marcar como entregado '
                'pedidos que estén en estado "Listo"'
            )

        }, status=400)

    comanda.estado = Comanda.Estados.ENTREGADO

    comanda.save()

    return JsonResponse({

        'ok': True,

        'estado': comanda.estado
    })
