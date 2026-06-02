import pytest
from django.urls import reverse

from apps.domicilios.models import PedidoDomicilio


@pytest.mark.django_db
def test_crear_pedido_exitoso(client, restaurante, producto):

    url = reverse(
        'crear_pedido_domicilio',
        kwargs={'slug': restaurante.slug}
    )

    payload = {
        "cliente_nombre": "Jefferson",
        "cliente_telefono": "3001234567",
        "direccion": "Pasto Centro",
        "referencia": "Casa azul",
        "items": [
            {
                "producto_id": producto.id,
                "cantidad": 2,
                "nota": "Sin cebolla"
            }
        ]
    }

    response = client.post(
        url,
        data=payload,
        content_type='application/json'
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True

    pedido = PedidoDomicilio.objects.first()

    assert pedido is not None
    assert pedido.cliente_nombre == "Jefferson"
    assert pedido.total == 30000
    
    
    
@pytest.mark.django_db
def test_restaurante_cerrado_no_permite_pedido(
    client,
    restaurante,
    producto
    ):

    restaurante.estado = restaurante.Estados.CERRADO
    restaurante.save()

    url = reverse(
        "crear_pedido_domicilio",
        args=[restaurante.slug]
    )

    payload = {
        "cliente_nombre": "Jefferson",
        "cliente_telefono": "3001234567",
        "direccion": "Calle 123",
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
    assert "cerrado" in data["error"]
    


@pytest.mark.django_db
def test_formulario_sin_referencia_permite_pedido(
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
        "cliente_telefono": "3001234567",
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

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True

    pedido = PedidoDomicilio.objects.first()

    assert pedido is not None
    assert pedido.cliente_nombre == "Jefferson"
    assert pedido.direccion == "Pasto Centro"
    assert pedido.referencia == ""

@pytest.mark.django_db
def test_campos_obligatorios_vacios(
    client,
    restaurante
):

    url = reverse(
        "crear_pedido_domicilio",
        args=[restaurante.slug]
    )

    payload = {
        "cliente_nombre": "",
        "cliente_telefono": "",
        "direccion": "",
        "items": []
    }

    response = client.post(
        url,
        data=payload,
        content_type="application/json"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["ok"] is False
    assert "obligatorios" in data["error"]
    
    
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
    assert "teléfono" in data["error"]