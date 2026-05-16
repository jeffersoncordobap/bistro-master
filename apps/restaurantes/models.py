from django.db import models
from django.core.validators import RegexValidator
from django.utils.text import slugify

solo_numeros = RegexValidator(
    regex=r'^\d+$',
    message='Solo se permiten números.'
)

class Restaurante(models.Model):

    class Estados(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        CERRADO = 'cerrado', 'Cerrado'

    nombre = models.CharField(max_length=100)

    slug = models.SlugField(
        unique=True
    )
    
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
