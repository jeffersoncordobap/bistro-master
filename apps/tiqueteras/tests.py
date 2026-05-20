from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from apps.restaurantes.models import Restaurante
from apps.usuarios.models import Usuario
from apps.tiqueteras.models import PlanTiquetera, Tiquetera, ConsumoTiquetera
from apps.comandas.models import Comanda

class TiqueterasSprint2TestCase(TestCase):

    def setUp(self):
        self.client = Client()
        
        # 1. Crear dependencias básicas
        self.restaurante = Restaurante.objects.create(nombre="Bistro Test", slug="bistro-test")
        
        self.usuario_mesero = Usuario.objects.create_user(
            username="mesero1",
            email="m1@bistro.com",
            password="password123",
            is_staff=True,
            rol=Usuario.Roles.MESERO,
            restaurante = self.restaurante,
            cedula="87654321",
        )

        self.usuario_admin = Usuario.objects.create_user(
            username="admin1",
            email="a1@bistro.com",
            password="password123",
            is_staff=True,
            rol=Usuario.Roles.ADMIN,
            restaurante=self.restaurante,
            cedula="12345678",
        )
        
        # 2. Crear Plan y Tiquetera base para pruebas
        self.plan = PlanTiquetera.objects.create(
            restaurante=self.restaurante,
            nombre="Plan 10 Almuerzos",
            precio=120000.00,
            cantidad_consumos=10,
            dias_vigencia=30
        )
        
        self.tiquetera = Tiquetera.objects.create(
            restaurante=self.restaurante,
            plan=self.plan,
            cliente_nombre="Juan Pérez",
            cliente_telefono="3001234567",
            fecha_inicio=timezone.now().date(),
            fecha_vencimiento=timezone.now().date() + timedelta(days=30)
        )

    # --- PRUEBAS HU-09 & HU-10 (Registro de Consumo y Descuento) ---
    def test_registro_consumo_exitoso_y_descuento_saldo(self):
        """ HU-09 y HU-10: Al registrar consumo, el saldo disminuye en 1 y se genera auditoría """
        # Creamos una comanda simulada tipo tiquetera
        comanda = Comanda.objects.create(
            restaurante=self.restaurante,
            mesero=self.usuario_mesero,
            numero_mesa=5,
            tipo_consumo='tiquetera',
            tiquetera=self.tiquetera
        )
        
        # Ejecutamos la acción del backend mediante su método nativo
        saldo_inicial = self.tiquetera.saldo_consumos
        self.tiquetera.consumir(cantidad=1)
        
        # Registramos la auditoría
        consumo = ConsumoTiquetera.objects.create(
            tiquetera=self.tiquetera,
            comanda=comanda,
            cantidad=1,
            registrado_por=self.usuario_mesero
        )

        # Aserciones
        self.assertEqual(self.tiquetera.saldo_consumos, saldo_inicial - 1)
        self.assertEqual(consumo.cantidad, 1)
        self.assertEqual(consumo.registrado_por, self.usuario_mesero)
        self.assertIsNotNone(consumo.fecha)

    def test_no_permite_consumo_si_saldo_es_cero(self):
        """ HU-10: El backend debe lanzar ValidationError si el saldo es insuficiente """
        # Forzamos saldo a 0 consumiendo el total
        self.tiquetera.consumir(cantidad=10)
        self.assertEqual(self.tiquetera.saldo_consumos, 0)
        
        # Intentar un consumo extra debe fallar
        with self.assertRaises(ValidationError):
            self.tiquetera.consumir(cantidad=1)

    def test_tiquetera_no_vigente_si_esta_vencida(self):
        """ HU-10: Una tiquetera con fecha vencida no debe permitir consumos """
        tiquetera_vencida = Tiquetera.objects.create(
            restaurante=self.restaurante,
            plan=self.plan,
            cliente_nombre="Cliente Antiguo",
            fecha_inicio=timezone.now().date() - timedelta(days=40),
            fecha_vencimiento=timezone.now().date() - timedelta(days=10)
        )
        
        self.assertFalse(tiquetera_vencida.esta_vigente)
        with self.assertRaises(ValidationError):
            tiquetera_vencida.consumir(1)

    # --- PRUEBAS HU-11 (Historial y Auditoría) ---
    def test_vista_historial_auditoria_filtros(self):
        """ HU-11: Validación de acceso y filtrado en la vista de auditoría """
        # Simulamos un consumo previo
        ConsumoTiquetera.objects.create(
            tiquetera=self.tiquetera,
            cantidad=1,
            registrado_por=self.usuario_mesero
        )
        
        # Logueamos al administrador (forzosamente, para tema de pruebas únicamente)
        self.client.force_login(self.usuario_admin)
        
        url = reverse('listar_tiqueteras') 
        
        # GET con filtros de búsqueda por nombre de cliente
        response = self.client.get(url, {'cliente': 'Juan'})
        
        self.assertEqual(response.status_code, 200)
        # Verifica que los datos del cliente existan en el contexto devuelto
        self.assertContains(response, "Juan Pérez")