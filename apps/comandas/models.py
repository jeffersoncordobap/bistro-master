from django.db import models
from apps.restaurantes.models import Restaurante
from apps.usuarios.models import Usuario
from apps.productos.models import Producto


class TipoConsumo(models.TextChoices):

    NORMAL = 'normal', 'Normal'
    TIQUETERA = 'tiquetera', 'Tiquetera'

class Comanda(models.Model):

    class Estados(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_PREPARACION = 'en_preparacion', 'En preparación'
        LISTO = 'listo', 'Listo'
        ENTREGADO = 'entregado', 'Entregado'

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='comandas'
    )
    mesero = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='comandas'
    )
    numero_mesa = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.PENDIENTE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    tipo_consumo = models.CharField(
        max_length=20,
        choices=TipoConsumo.choices,
        default=TipoConsumo.NORMAL
    )
    
    tiquetera = models.ForeignKey(
    'tiqueteras.Tiquetera',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comandas'
    )

    def __str__(self):
        return f'Mesa {self.numero_mesa} - {self.estado}'


class ItemComanda(models.Model):
    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField(default=1)
    nota = models.TextField(blank=True)

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre}'
    
    
