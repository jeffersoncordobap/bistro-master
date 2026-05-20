from django.test import TestCase, Client
from django.urls import reverse
from apps.restaurantes.models import Restaurante
from apps.usuarios.models import Usuario
from apps.comandas.models import Comanda

class ComandasTiempoRealTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.restaurante = Restaurante.objects.create(nombre="Bistro Test", slug="bistro-test")
        
        self.usuario_admin = Usuario.objects.create_user(
            username="admin1",
            email="a1@bistro.com",
            password="password123",
            is_staff=True,
            rol=Usuario.Roles.ADMIN,
            restaurante=self.restaurante,
            cedula="12345678"
        )

        self.usuario_mesero = Usuario.objects.create_user(
            username="mesero1",
            email="m1@bistro.com",
            password="password123",
            rol=Usuario.Roles.MESERO,
            restaurante=self.restaurante,
            cedula="87654321"
        )
        
        # Crear comanda inicial pendiente
        self.comanda = Comanda.objects.create(
            restaurante=self.restaurante,
            mesero=self.usuario_mesero,
            numero_mesa=3,
            estado=Comanda.Estados.PENDIENTE
        )
        
        self.client.force_login(self.usuario_admin)

    # --- PRUEBAS HU-12 (Gestión en Tiempo Real) ---
    def test_dashboard_lista_pedidos_activos(self):
        """ HU-12: El endpoint del dashboard debe retornar las comandas activas """
        url = reverse('api_panel_pedidos')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Si respondes con JSON, validamos la estructura
        self.assertIn('comandas', response.json())
        self.assertEqual(response.json()['comandas'][0]['mesa'], 3)

    def test_cambio_estado_pedido_desde_dashboard(self):
        """ HU-12: Un clic en el dashboard debe modificar el estado en el backend """
        # Suponiendo que tu endpoint recibe el ID y el nuevo estado
        url = reverse('cambiar_estado_comanda', kwargs={'comanda_id': self.comanda.pk})
        
        # Enviamos el cambio a 'En preparación'
        response = self.client.post(
            url, 
            {'estado': Comanda.Estados.EN_PREPARACION},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Recargamos de la base de datos
        self.comanda.refresh_from_db()
        self.assertEqual(self.comanda.estado, Comanda.Estados.EN_PREPARACION)