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

    # ── Información básica ──
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

    # ── Apariencia ──
    slogan = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Frase corta que describe tu restaurante.'
    )

    logo = models.ImageField(
        upload_to='restaurantes/logos/',
        blank=True,
        null=True,
        help_text='Logo del restaurante.'
    )

    portada = models.ImageField(
        upload_to='restaurantes/portadas/',
        blank=True,
        null=True,
        help_text='Imagen de fondo del banner principal.'
    )

    color_principal = models.CharField(
        max_length=7,
        default='#e74c3c',
        help_text='Color principal en formato HEX (ej: #e74c3c).'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre