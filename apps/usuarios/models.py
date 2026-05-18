from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from apps.restaurantes.models import Restaurante

solo_numeros = RegexValidator(
    regex=r'^\d+$',
    message='Solo se permiten números.'
)

class Usuario(AbstractUser):
    
    REQUIRED_FIELDS = ['email', 'cedula', 'telefono']
    
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        MESERO = 'mesero', 'Mesero'
        DOMICILIARIO = 'domiciliario', 'Domiciliario'

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='usuarios',
        null=True,
        blank=True
    )

    cedula = models.CharField(
        max_length=20,
        validators=[solo_numeros]
    )

    telefono = models.CharField(
        max_length=20,
        validators=[solo_numeros]
    )

    
    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        null=True,
        blank=True
    )
    
    email = models.EmailField(
    unique=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['restaurante', 'cedula'],
                name='cedula_unica_por_restaurante'
            )
        ]

    def __str__(self):
        return self.username