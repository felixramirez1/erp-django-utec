"""Suite de pruebas W15 — Webhook de Stripe y lógica de pedidos.

Usa unittest.mock.patch para simular stripe.Webhook.construct_event
sin requerir claves reales ni conexión a Stripe.

Ejecutar con:
    python manage.py test tests.test_w15_webhooks --verbosity=2

Resultado esperado:
    Ran 8 tests in X.XXXs
    OK
"""
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse

from clientes.models    import Cliente
from configuracion.models import ConfiguracionERP
from productos.models   import Categoria, Producto
from ventas.models      import Pedido


def _crear_evento(tipo: str, pedido_id: int) -> dict:
    """Construye un evento Stripe simulado para tests."""
    return {
        'type': tipo,
        'data': {
            'object': {
                'id':       f'pi_test_{pedido_id}',
                'amount':   116000,
                'currency': 'mxn',
                'status':   'succeeded' if 'succeeded' in tipo else 'failed',
                'metadata': {'pedido_id': str(pedido_id)},
            }
        }
    }


def _crear_pedido_con_snapshot(cliente, producto, cantidad=2) -> Pedido:
    """Crea un Pedido con items_snapshot para los tests."""
    return Pedido.objects.create(
        numero_pedido  = 'PED-2025-TEST',
        cliente        = cliente,
        estado         = 'pendiente',
        total_pagado   = Decimal('1000.00'),
        items_snapshot = [
            {
                'producto_id': producto.pk,
                'nombre':      producto.nombre,
                'cantidad':    cantidad,
                'precio':      str(producto.precio),
            }
        ]
    )


class WebhookSegurityTest(TestCase):
    """Tests de seguridad del endpoint webhook."""

    def test_get_rechazado_con_405(self):
        """El webhook solo acepta POST → GET devuelve 405."""
        r = self.client.get(reverse('catalogo:webhook'))
        self.assertEqual(r.status_code, 405)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_firma_invalida_devuelve_400(self, mock_construct):
        """Firma inválida → 400 Bad Request."""
        import stripe
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            'Test error', 'sig_header'
        )
        r = self.client.post(
            reverse('catalogo:webhook'),
            data=b'{"fake": "payload"}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=fake,v1=invalid'
        )
        self.assertEqual(r.status_code, 400)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_payload_invalido_devuelve_400(self, mock_construct):
        """Payload malformado → 400 Bad Request."""
        mock_construct.side_effect = ValueError('JSON inválido')
        r = self.client.post(
            reverse('catalogo:webhook'),
            data=b'no es json',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=123,v1=abc'
        )
        self.assertEqual(r.status_code, 400)


class WebhookPagoExitosoTest(TestCase):
    """Tests del manejo de payment_intent.succeeded."""

    def setUp(self):
        ConfiguracionERP.get_instance()
        cat         = Categoria.objects.create(nombre='Cat')
        self.prod   = Producto.objects.create(
            nombre='P', precio=Decimal('500.00'), stock=10, categoria=cat
        )
        self.cli    = Cliente.objects.create(nombre='C', correo='c@t.com')
        self.pedido = _crear_pedido_con_snapshot(
            self.cli, self.prod, cantidad=2
        )

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_payment_succeeded_actualiza_estado(self, mock_construct):
        """payment_intent.succeeded → Pedido.estado cambia a 'pagado'."""
        mock_construct.return_value = _crear_evento(
            'payment_intent.succeeded', self.pedido.pk
        )
        r = self.client.post(
            reverse('catalogo:webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=123,v1=ok'
        )
        self.assertEqual(r.status_code, 200)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'pagado')

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_payment_succeeded_descuenta_stock(self, mock_construct):
        """payment_intent.succeeded → stock decrementado en 2 unidades."""
        stock_inicial = self.prod.stock   # 10
        mock_construct.return_value = _crear_evento(
            'payment_intent.succeeded', self.pedido.pk
        )
        self.client.post(
            reverse('catalogo:webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=123,v1=ok'
        )
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.stock, stock_inicial - 2)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_payment_succeeded_idempotente(self, mock_construct):
        """Segundo webhook del mismo pago → estado no cambia (idempotente)."""
        self.pedido.estado = 'pagado'
        self.pedido.save()
        stock_antes = self.prod.stock

        mock_construct.return_value = _crear_evento(
            'payment_intent.succeeded', self.pedido.pk
        )
        self.client.post(
            reverse('catalogo:webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=123,v1=ok'
        )
        self.prod.refresh_from_db()
        # El stock no debe cambiar porque ya estaba pagado
        self.assertEqual(self.prod.stock, stock_antes)


class WebhookPagoFallidoTest(TestCase):
    """Tests del manejo de payment_intent.payment_failed."""

    def setUp(self):
        cat         = Categoria.objects.create(nombre='Cat')
        prod        = Producto.objects.create(
            nombre='P', precio=Decimal('100.00'), stock=5, categoria=cat
        )
        cli         = Cliente.objects.create(nombre='C', correo='c2@t.com')
        self.pedido = _crear_pedido_con_snapshot(cli, prod)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_payment_failed_cancela_pedido(self, mock_construct):
        """payment_intent.payment_failed → Pedido.estado = 'cancelado'."""
        mock_construct.return_value = _crear_evento(
            'payment_intent.payment_failed', self.pedido.pk
        )
        r = self.client.post(
            reverse('catalogo:webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=123,v1=ok'
        )
        self.assertEqual(r.status_code, 200)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'cancelado')


class WebhookStripeObjectTest(TestCase):
    """Regresión: con stripe >= 15 el evento real es un StripeObject
    (no un dict). Antes provocaba HTTP 500 en producción."""

    def setUp(self):
        cat         = Categoria.objects.create(nombre='Cat')
        self.prod   = Producto.objects.create(
            nombre='P', precio=Decimal('500.00'), stock=10, categoria=cat
        )
        cli         = Cliente.objects.create(nombre='C', correo='c3@t.com')
        self.pedido = _crear_pedido_con_snapshot(cli, self.prod, cantidad=2)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_evento_stripe_object_real(self, mock_construct):
        """StripeObject real → 200, pedido 'pagado' y stock descontado."""
        import stripe
        datos = _crear_evento('payment_intent.succeeded', self.pedido.pk)
        datos['data']['object']['object'] = 'payment_intent'
        datos.update({'id': 'evt_test', 'object': 'event'})
        mock_construct.return_value = stripe.Event.construct_from(datos, 'sk_test')

        r = self.client.post(
            reverse('catalogo:webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=123,v1=ok'
        )
        self.assertEqual(r.status_code, 200)
        self.pedido.refresh_from_db()
        self.prod.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'pagado')
        self.assertEqual(self.prod.stock, 8)