from django.db import models
from apps.restaurantes.models import Restaurante
from django.core.validators import MinValueValidator

class CategoriaProducto(models.Model):

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='categorias'
    )

    nombre = models.CharField(
        max_length=100
    )

    activa = models.BooleanField(
        default=True
    )

    class Meta:

        unique_together = (
            'restaurante',
            'nombre'
        )

        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Producto(models.Model):

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='productos'
    )

    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    precio = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    validators=[
        MinValueValidator(1000)
        ]
    )

    imagen = models.ImageField(
        upload_to='productos/',
        null=True,
        blank=True
    )

    disponible = models.BooleanField(
        default=True
    )

    control_stock = models.BooleanField(
        default=False
    )

    stock = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    cantidad_maxima_por_pedido = models.PositiveIntegerField(
        default=20
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre
    
    def descontar_stock(self, cantidad=1):
        if self.control_stock and self.stock is not None:
            if cantidad > self.stock:
                raise ValueError(f'No hay suficiente stock disponible, solo quedan {self.stock} unidades de {self.nombre}.')
            self.stock -= cantidad
            if self.stock == 0:
                self.disponible = False
            self.save()