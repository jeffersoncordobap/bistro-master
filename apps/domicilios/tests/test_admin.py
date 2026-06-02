import pytest

from django.urls import reverse

from apps.domicilios.models import PedidoDomicilio


@pytest.mark.django_db
def test_visualizar_domicilio_en_panel(
    client,
    admin,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto",
        total=15000,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        estado_entrega=PedidoDomicilio.EstadosEntrega.RECIBIDO,
    )

    client.login(
        username="admin",
        password="1234"
    )

    url = reverse("panel_domicilios")

    response = client.get(url)

    assert response.status_code == 200

    assert pedido in response.context["pedidos"]
    
    
@pytest.mark.django_db
def test_cambiar_estado_a_preparacion(
    client,
    admin,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto",
        total=15000,
        estado=PedidoDomicilio.Estados.PENDIENTE,
    )

    client.login(
        username="admin",
        password="1234"
    )

    url = reverse(
        "cambiar_estado_pedido_domicilio",
        args=[pedido.id]
    )

    response = client.post(
        url,
        {
            "estado": PedidoDomicilio.Estados.EN_PREPARACION
        }
    )

    assert response.status_code == 200

    pedido.refresh_from_db()

    assert pedido.estado == PedidoDomicilio.Estados.EN_PREPARACION


@pytest.mark.django_db
def test_cambiar_estado_a_listo(
    client,
    admin,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto",
        total=15000,
        estado=PedidoDomicilio.Estados.PENDIENTE,
    )

    client.login(
        username="admin",
        password="1234"
    )

    url = reverse(
        "cambiar_estado_pedido_domicilio",
        args=[pedido.id]
    )

    response = client.post(
        url,
        {
            "estado": PedidoDomicilio.Estados.LISTO
        }
    )

    assert response.status_code == 200

    pedido.refresh_from_db()

    assert pedido.estado == PedidoDomicilio.Estados.LISTO
    
    
    
    
@pytest.mark.django_db
def test_cambiar_estado_a_entregado(
    client,
    admin,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto",
        total=15000,
        estado=PedidoDomicilio.Estados.PENDIENTE,
    )

    client.login(
        username="admin",
        password="1234"
    )

    url = reverse(
        "cambiar_estado_pedido_domicilio",
        args=[pedido.id]
    )

    response = client.post(
        url,
        {
            "estado": PedidoDomicilio.Estados.ENTREGADO
        }
    )

    assert response.status_code == 200

    pedido.refresh_from_db()

    assert pedido.estado == PedidoDomicilio.Estados.ENTREGADO