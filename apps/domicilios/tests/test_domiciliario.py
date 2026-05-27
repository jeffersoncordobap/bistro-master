import pytest

from django.urls import reverse

from apps.domicilios.models import PedidoDomicilio


@pytest.mark.django_db
def test_enviar_mensaje_whatsapp(
    client,
    domiciliario,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        domiciliario=domiciliario,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto",
        total=15000,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        estado_entrega=PedidoDomicilio.EstadosEntrega.RECIBIDO,
    )

    client.login(
        username="domi",
        password="1234"
    )

    url = reverse(
        "domiciliario_marcar_en_camino",
        args=[pedido.id]
    )

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True

    assert "whatsapp_url" in data

    pedido.refresh_from_db()

    assert (
        pedido.estado_entrega
        == PedidoDomicilio.EstadosEntrega.EN_CAMINO
    )
    
    
    
@pytest.mark.django_db
def test_telefono_invalido(
    client,
    restaurante,
    producto
):

    url = reverse(
        "crear_pedido_domicilio",
        args=[restaurante.slug]
    )

    payload = {
        "cliente_nombre": "Jefferson",
        "cliente_telefono": "telefono_fake",
        "direccion": "Pasto Centro",
        "items": [
            {
                "producto_id": producto.id,
                "cantidad": 1
            }
        ]
    }

    response = client.post(
        url,
        data=payload,
        content_type="application/json"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["ok"] is False

    assert (
        data["error"]
        == "El teléfono debe ser numérico."
    )
    
    
@pytest.mark.django_db
def test_visualizar_pedidos_asignados(
    client,
    domiciliario,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        domiciliario=domiciliario,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto",
        total=20000,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        estado_entrega=PedidoDomicilio.EstadosEntrega.RECIBIDO,
    )

    client.login(
        username="domi",
        password="1234"
    )

    url = reverse(
        "domiciliario_mis_domicilios"
    )

    response = client.get(url)

    assert response.status_code == 200

    pedidos = response.context["pedidos"]

    assert pedido in pedidos
    
    
@pytest.mark.django_db
def test_sin_pedidos_asignados(
    client,
    domiciliario
):

    client.login(
        username="domi",
        password="1234"
    )

    url = reverse(
        "domiciliario_mis_domicilios"
    )

    response = client.get(url)

    assert response.status_code == 200

    pedidos = response.context["pedidos"]

    assert len(pedidos) == 0
    
    
@pytest.mark.django_db
def test_visualizar_informacion_cliente(
    client,
    domiciliario,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        domiciliario=domiciliario,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto Centro",
        total=20000,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        estado_entrega=PedidoDomicilio.EstadosEntrega.RECIBIDO,
    )

    client.login(
        username="domi",
        password="1234"
    )

    url = reverse(
        "domiciliario_mis_domicilios"
    )

    response = client.get(url)

    pedidos = response.context["pedidos"]

    pedido_response = pedidos.first()

    assert (
        pedido_response.cliente_nombre
        == "Jefferson"
    )

    assert (
        pedido_response.cliente_telefono
        == "3001234567"
    )

    assert (
        pedido_response.direccion
        == "Pasto Centro"
    )
    
@pytest.mark.django_db
def test_acceso_restringido_usuario_no_domiciliario(
    client,
    admin
):

    client.force_login(admin)

    url = reverse(
        "domiciliario_mis_domicilios"
    )

    response = client.get(url)

    assert response.status_code == 302

    assert "/login/" in response.url
    
    
@pytest.mark.django_db
def test_marcar_pedido_entregado(
    client,
    domiciliario,
    restaurante
):

    pedido = PedidoDomicilio.objects.create(
        restaurante=restaurante,
        domiciliario=domiciliario,
        cliente_nombre="Jefferson",
        cliente_telefono="3001234567",
        direccion="Pasto",
        total=15000,
        estado=PedidoDomicilio.Estados.ENTREGADO,
        estado_entrega=PedidoDomicilio.EstadosEntrega.EN_CAMINO,
    )

    client.login(
        username="domi",
        password="1234"
    )

    url = reverse(
        "domiciliario_marcar_entregado",
        args=[pedido.id]
    )

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True

    pedido.refresh_from_db()

    assert (
        pedido.estado_entrega
        == PedidoDomicilio.EstadosEntrega.ENTREGADO
    )

    assert pedido.fecha_entregado is not None