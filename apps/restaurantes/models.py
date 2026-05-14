from django.db import models
from django.core.validators import RegexValidator

solo_numeros = RegexValidator(
    regex=r'^\d+$',
    message='Solo se permiten números.'
)

class Restaurante(models.Model):

    class Estados(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        CERRADO = 'cerrado', 'Cerrado'

    nombre = models.CharField(max_length=100)

    nit = models.CharField(
        max_length=20,
        unique=True,
        validators=[solo_numeros]
    )

    direccion = models.CharField(max_length=200)

    telefono = models.CharField(
        max_length=20,
        validators=[solo_numeros]
    )

    estado = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.ABIERTO
    )

    def __str__(self):
        return self.nombre
