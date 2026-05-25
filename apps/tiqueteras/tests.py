from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.restaurantes.models import Restaurante

from .models import PlanTiquetera, Tiquetera, ConsumoTiquetera


User = get_user_model()


class HistorialTiqueterasTests(TestCase):

	def setUp(self):
		self.restaurante = Restaurante.objects.create(
			nombre='Bistro Central',
			slug='bistro-central',
			nit='900000001',
			direccion='Calle 1 # 2-3',
			telefono='3001234567'
		)

		self.admin = User.objects.create_user(
			username='admin',
			email='admin@bistro.com',
			password='password123',
			cedula='123456789',
			telefono='3001111111',
			rol=User.Roles.ADMIN,
			restaurante=self.restaurante
		)

		self.plan = PlanTiquetera.objects.create(
			restaurante=self.restaurante,
			nombre='Plan Almuerzo',
			descripcion='Plan principal',
			precio=100000,
			cantidad_consumos=10,
			dias_vigencia=30,
			tipo_servicio='almuerzo',
			activo=True
		)

		self.tiquetera_ana = Tiquetera.objects.create(
			restaurante=self.restaurante,
			plan=self.plan,
			cliente_nombre='Ana Perez',
			cliente_telefono='3010000001',
			fecha_inicio=timezone.now().date(),
			fecha_vencimiento=timezone.now().date() + timedelta(days=30),
			activa=True
		)

		self.tiquetera_carlos = Tiquetera.objects.create(
			restaurante=self.restaurante,
			plan=self.plan,
			cliente_nombre='Carlos Gomez',
			cliente_telefono='3010000002',
			fecha_inicio=timezone.now().date(),
			fecha_vencimiento=timezone.now().date() + timedelta(days=30),
			activa=True
		)

		self.transaccion_ana = ConsumoTiquetera.objects.create(
			tiquetera=self.tiquetera_ana,
			cantidad=1,
			registrado_por=self.admin
		)

		self.transaccion_carlos = ConsumoTiquetera.objects.create(
			tiquetera=self.tiquetera_carlos,
			cantidad=2,
			registrado_por=self.admin
		)

		fecha_ana = timezone.make_aware(datetime(2026, 5, 5, 10, 0, 0))
		fecha_carlos = timezone.make_aware(datetime(2026, 5, 15, 12, 0, 0))

		ConsumoTiquetera.objects.filter(pk=self.transaccion_ana.pk).update(
			fecha=fecha_ana
		)
		ConsumoTiquetera.objects.filter(pk=self.transaccion_carlos.pk).update(
			fecha=fecha_carlos
		)

		self.client.force_login(self.admin)

	def test_historial_muestra_transacciones(self):
		response = self.client.get(reverse('historial_tiqueteras'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Ana Perez')
		self.assertContains(response, 'Carlos Gomez')

	def test_filtra_por_nombre_de_cliente(self):
		response = self.client.get(
			reverse('historial_tiqueteras'),
			{'cliente': 'Ana'}
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Ana Perez')
		self.assertNotContains(response, 'Carlos Gomez')

	def test_filtra_por_rango_de_fechas(self):
		response = self.client.get(
			reverse('historial_tiqueteras'),
			{
				'fecha_inicio': '2026-05-14',
				'fecha_fin': '2026-05-16'
			}
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Carlos Gomez')
		self.assertNotContains(response, 'Ana Perez')

	def test_endpoint_es_solo_lectura(self):
		response = self.client.post(reverse('historial_tiqueteras'))

		self.assertEqual(response.status_code, 405)

	def test_buscar_tiquetera_endpoint(self):
		# buscar por nombre
		response = self.client.get(reverse('buscar_tiquetera'), {'q': 'Ana'})

		self.assertEqual(response.status_code, 200)

		data = response.json()

		self.assertIn('results', data)

		nombres = [r['cliente_nombre'] for r in data['results']]

		self.assertIn('Ana Perez', nombres)

	def test_buscar_por_codigo(self):
		# asignar un codigo conocido a una tiquetera
		self.tiquetera_ana.codigo = 'CODE12345'
		self.tiquetera_ana.save()

		response = self.client.get(reverse('buscar_tiquetera'), {'q': 'CODE12345'})

		self.assertEqual(response.status_code, 200)

		data = response.json()

		self.assertTrue(any(r['id'] == self.tiquetera_ana.id for r in data['results']))
