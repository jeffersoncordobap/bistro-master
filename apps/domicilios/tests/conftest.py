import pytest
from decimal import Decimal

from apps.restaurantes.models import Restaurante
from apps.productos.models import Producto
from apps.usuarios.models import Usuario


@pytest.fixture
def restaurante():
    return Restaurante.objects.create(
        nombre="Bistro",
        slug="bistro",
        estado=Restaurante.Estados.ABIERTO,
    )


@pytest.fixture
def producto(restaurante):
    return Producto.objects.create(
        restaurante=restaurante,
        nombre="Hamburguesa",
        precio=Decimal("15000"),
        disponible=True,
    )


@pytest.fixture
def admin(restaurante):
    return Usuario.objects.create_user(
        username="admin",
        password="1234",
        rol=Usuario.Roles.ADMIN,
        restaurante=restaurante,
    )


@pytest.fixture
def domiciliario(restaurante):
    return Usuario.objects.create_user(
        username="domi",
        password="1234",
        rol=Usuario.Roles.DOMICILIARIO,
        restaurante=restaurante,
    )