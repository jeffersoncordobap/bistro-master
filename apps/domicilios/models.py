from django.db import models

from apps.productos.models import Producto
from apps.restaurantes.models import Restaurante
from apps.usuarios.models import Usuario


class PedidoDomicilio(models.Model):

    class Estados(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_PREPARACION = 'en_preparacion', 'En preparación'
        LISTO = 'listo', 'Listo'
        ENTREGADO = 'entregado', 'Entregado'

    class EstadosEntrega(models.TextChoices):
        RECIBIDO = 'recibido', 'Pedido recibido'
        EN_CAMINO = 'en_camino', 'Pedido en camino'
        ENTREGADO = 'entregado', 'Pedido entregado'

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='pedidos_domicilio',
    )

    domiciliario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='domicilios_asignados',
        limit_choices_to={'rol': Usuario.Roles.DOMICILIARIO},
    )

    estado = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.PENDIENTE,
    )

    estado_entrega = models.CharField(
        max_length=20,
        choices=EstadosEntrega.choices,
        null=True,
        blank=True,
        default=None,
    )

    fecha_recibido = models.DateTimeField(null=True, blank=True)
    fecha_en_camino = models.DateTimeField(null=True, blank=True)
    fecha_entregado = models.DateTimeField(null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    cliente_nombre = models.CharField(max_length=150)

    cliente_telefono = models.CharField(max_length=20)

    direccion = models.CharField(max_length=255)

    referencia = models.TextField(blank=True, default='')

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return f'Domicilio #{self.pk} - {self.cliente_nombre}'


class ItemPedidoDomicilio(models.Model):

    pedido = models.ForeignKey(
        PedidoDomicilio,
        on_delete=models.CASCADE,
        related_name='items',
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='items_domicilio',
    )

    cantidad = models.PositiveIntegerField(default=1)

    nota = models.TextField(blank=True, default='')

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre}'
