from django.utils import timezone

from django.db import models
from django.core.exceptions import ValidationError

from apps.comandas.models import Comanda
from apps.restaurantes.models import Restaurante
from apps.usuarios.models import Usuario


class TipoServicio(models.TextChoices):
    ALMUERZO = 'almuerzo', 'Almuerzo'
    CENA = 'cena', 'Cena'


class PlanTiquetera(models.Model):

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='planes_tiquetera'
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cantidad_consumos = models.PositiveIntegerField()

    dias_vigencia = models.PositiveIntegerField()

    permite_multiples_consumos = models.BooleanField(
        default=False
    )

    activo = models.BooleanField(
        default=True
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )
    
    tipo_servicio = models.CharField(
        max_length=20,
        choices=TipoServicio.choices,
        default=TipoServicio.ALMUERZO
    )
    
    def __str__(self):
        return self.nombre
   
class Tiquetera(models.Model):

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='tiqueteras'
    )

    plan = models.ForeignKey(
        PlanTiquetera,
        on_delete=models.PROTECT
    )

    cliente_nombre = models.CharField(
        max_length=150
    )

    cliente_telefono = models.CharField(
        max_length=20,
        blank=True
    )

    saldo_consumos = models.PositiveIntegerField(editable=False)

    fecha_inicio = models.DateField()

    fecha_vencimiento = models.DateField()

    activa = models.BooleanField(
        default=True
    )

    creada = models.DateTimeField(
        auto_now_add=True
    )
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.saldo_consumos = self.plan.cantidad_consumos
        super().save(*args, **kwargs)
    
    
    def clean(self):
        if self.fecha_vencimiento <= self.fecha_inicio:
            raise ValidationError(
                'La fecha de vencimiento debe ser mayor a la fecha de inicio.'
            )
            
    @property
    def esta_vigente(self):
        return (
            self.activa and
            self.saldo_consumos > 0 and
            self.fecha_vencimiento >= timezone.now().date()
        )
    
    def __str__(self):
        return f'{self.cliente_nombre} - {self.plan.nombre}'
    
class ConsumoTiquetera(models.Model):

    tiquetera = models.ForeignKey(
        Tiquetera,
        on_delete=models.CASCADE,
        related_name='consumos'
    )

    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    cantidad = models.PositiveIntegerField(
        default=1
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True
    )
    
    def __str__(self):
        return f'{self.tiquetera.cliente_nombre} - {self.cantidad} consumo(s)'
    