"""Suite de pruebas W16 — Celery worker y tareas asíncronas.

Verifica la configuración de Celery, la definición de las tareas
y su invocación desde las vistas.

Ejecutar con:
    python manage.py test tests.test_w16_celery --verbosity=2

Resultado esperado:
    Ran 8 tests in X.XXXs
    OK
"""
from decimal import Decimal
from unittest.mock import call, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from clientes.models      import Cliente
from configuracion.models import ConfiguracionERP
from productos.models     import Categoria, Producto
from ventas.models        import Pedido
from ventas.tasks         import (
    enviar_confirmacion_pedido,
    verificar_stock_bajo,
)


class CeleryConfigTest(TestCase):
    """Verifica que Celery está correctamente configurado."""

    def test_celery_app_importable(self):
        """La app Celery debe poder importarse sin errores."""
        from core.celery import app as celery_app
        self.assertIsNotNone(celery_app)
        self.assertEqual(celery_app.main, 'core')

    def test_tareas_registradas_en_celery(self):
        """Las tareas de ventas deben estar registradas en Celery."""
        from core.celery import app as celery_app
        tareas = celery_app.tasks.keys()
        self.assertIn('ventas.enviar_confirmacion_pedido', tareas)
        self.assertIn('ventas.verificar_stock_bajo', tareas)


class EnviarConfirmacionTareaTest(TestCase):
    """Tests de la tarea enviar_confirmacion_pedido."""

    def setUp(self):
        ConfiguracionERP.get_instance()
        cat         = Categoria.objects.create(nombre='Cat')
        prod        = Producto.objects.create(
            nombre='P', precio=Decimal('100.00'), stock=5, categoria=cat
        )
        cli         = Cliente.objects.create(nombre='C', correo='c@t.com')
        self.pedido = Pedido.objects.create(
            numero_pedido = 'PED-2025-0001',
            cliente       = cli,
            estado        = 'pagado',
            total_pagado  = Decimal('116.00'),
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_tarea_ejecuta_y_retorna_ok(self):
        """La tarea debe ejecutarse y retornar estado 'ok'."""
        resultado = enviar_confirmacion_pedido.delay(self.pedido.pk)
        data = resultado.get()
        self.assertEqual(data['estado'], 'ok')
        self.assertEqual(data['pedido_id'], self.pedido.pk)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_tarea_con_pedido_inexistente_retorna_error(self):
        """La tarea con pedido inexistente debe retornar estado 'error'."""
        resultado = enviar_confirmacion_pedido.delay(9999)
        data = resultado.get()
        self.assertEqual(data['estado'], 'error')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_verificar_stock_bajo_detecta_productos(self):
        """verificar_stock_bajo debe detectar productos con stock < umbral."""
        Producto.objects.filter(nombre='P').update(stock=3)
        resultado = verificar_stock_bajo.delay(umbral=5)
        data = resultado.get()
        self.assertGreaterEqual(data['total'], 1)
        nombres = [p['nombre'] for p in data['productos_bajos']]
        self.assertIn('P', nombres)


class TareaInvocadaDesdeVistaTest(TestCase):
    """Verifica que las vistas invocan las tareas con .delay()."""

    def setUp(self):
        ConfiguracionERP.get_instance()
        cat  = Categoria.objects.create(nombre='Cat')
        cli  = Cliente.objects.create(nombre='C', correo='test@test.com')
        self.pedido = Pedido.objects.create(
            numero_pedido = 'PED-2025-VISTA',
            cliente       = cli,
            estado        = 'pendiente',
            total_pagado  = Decimal('100.00'),
        )
        self.user = User.objects.create_user('viewer', password='pass')

    @patch('catalogo.views.enviar_confirmacion_pedido.delay')
    def test_pago_exitoso_llama_a_delay(self, mock_delay):
        """pago_exitoso() debe llamar a .delay() con el pedido_id."""
        self.client.force_login(self.user)
        self.client.get(
            reverse('catalogo:pago_exitoso', args=[self.pedido.pk])
        )
        mock_delay.assert_called_once_with(self.pedido.pk)

    @patch('catalogo.webhook_views.enviar_confirmacion_pedido.delay')
    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_webhook_succeeded_llama_a_delay(
        self, mock_event, mock_delay
    ):
        """El webhook payment_intent.succeeded debe llamar a .delay()."""
        mock_event.return_value = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test',
                    'metadata': {'pedido_id': str(self.pedido.pk)},
                }
            }
        }
        self.pedido.items_snapshot = []
        self.pedido.save()

        self.client.post(
            reverse('catalogo:webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1,v1=ok'
        )
        mock_delay.assert_called_once_with(self.pedido.pk)