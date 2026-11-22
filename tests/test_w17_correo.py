"""Suite de pruebas W17 — Correos transaccionales con django-anymail.

Usa el backend locmem (en memoria) para capturar correos sin enviarlos.
Los correos enviados se almacenan en django.core.mail.outbox.
NO se conecta a SendGrid ni a Redis (laboratorio sin Docker).

Ejecutar con:
    python manage.py test tests.test_w17_correo --verbosity=2

Resultado esperado:
    Ran 12 tests in X.XXXs
    OK
"""
from decimal import Decimal
from unittest.mock import patch

from celery.exceptions import Retry

from django.core import mail
from django.test import TestCase, override_settings

from clientes.models      import Cliente
from configuracion.models import ConfiguracionERP
from productos.models     import Categoria, Producto
from ventas.models        import Pedido
from ventas.tasks         import (
    enviar_confirmacion_pedido,
    verificar_stock_bajo,
)

# Configuración común para todos los tests de correo
EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'CELERY_TASK_ALWAYS_EAGER': True,
    'CELERY_TASK_EAGER_PROPAGATES': True,
    'ADMINS': [('Admin Test', 'admin@test.com')],
    'DEFAULT_FROM_EMAIL': 'test@erp.com',
    'SITE_URL': 'https://erp-test.onrender.com',
}


def _crear_pedido_pagado(correo_enviado=False, nombre_cliente='Cliente Test',
                         precio='100.00', cantidad=2) -> Pedido:
    """Crea un Pedido en estado 'pagado' para los tests."""
    ConfiguracionERP.get_instance()
    n    = Pedido.objects.count()
    cat  = Categoria.objects.create(nombre=f'Cat-{n}')
    prod = Producto.objects.create(
        nombre='Producto Test', precio=Decimal(precio),
        stock=5, categoria=cat
    )
    cli  = Cliente.objects.create(
        nombre=nombre_cliente,
        correo=f'cliente{n}@test.com'
    )
    return Pedido.objects.create(
        numero_pedido  = f'PED-TEST-{n:03d}',
        cliente        = cli,
        estado         = 'pagado',
        total_pagado   = Decimal('116.00'),
        correo_enviado = correo_enviado,
        items_snapshot = [
            {
                'producto_id': prod.pk,
                'nombre':      prod.nombre,
                'cantidad':    cantidad,
                'precio':      str(prod.precio),
            }
        ],
    )


@override_settings(**EMAIL_SETTINGS)
class EnviarConfirmacionTest(TestCase):
    """Tests del envío del correo de confirmación de pedido."""

    def setUp(self):
        mail.outbox = []   # limpiar la bandeja de prueba antes de cada test

    def test_correo_enviado_a_cliente(self):
        """El correo debe enviarse al correo del cliente."""
        pedido = _crear_pedido_pagado()
        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(pedido.cliente.correo, mail.outbox[0].to)

    def test_correo_asunto_contiene_numero_pedido(self):
        """El asunto debe incluir el número de pedido."""
        pedido = _crear_pedido_pagado()
        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertIn(pedido.numero_pedido, mail.outbox[0].subject)

    def test_correo_cuerpo_html_contiene_total(self):
        """El cuerpo HTML debe contener el total pagado."""
        pedido = _crear_pedido_pagado()
        enviar_confirmacion_pedido.delay(pedido.pk)

        mensaje = mail.outbox[0]
        alternativas = [
            body for body, mime in mensaje.alternatives
            if mime == 'text/html'
        ]
        self.assertEqual(len(alternativas), 1)
        self.assertIn(str(pedido.total_pagado), alternativas[0])

    def test_correo_marca_correo_enviado_true(self):
        """Tras el envío, Pedido.correo_enviado debe ser True."""
        pedido = _crear_pedido_pagado()
        self.assertFalse(pedido.correo_enviado)

        enviar_confirmacion_pedido.delay(pedido.pk)

        pedido.refresh_from_db()
        self.assertTrue(pedido.correo_enviado)

    def test_correo_no_duplicado_si_ya_enviado(self):
        """Si correo_enviado=True, la tarea NO debe enviar otro correo."""
        pedido = _crear_pedido_pagado(correo_enviado=True)

        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertEqual(len(mail.outbox), 0)

    def test_tarea_devuelve_skip_si_ya_enviado(self):
        """La tarea debe devolver estado 'skip' si ya se envió."""
        pedido = _crear_pedido_pagado(correo_enviado=True)
        resultado = enviar_confirmacion_pedido.delay(pedido.pk).get()
        self.assertEqual(resultado['estado'], 'skip')

    # ── Pruebas de regresión agregadas en la verificación de W17 ─────────

    def test_subtotal_conserva_centavos_y_url_usa_site_url(self):
        """Subtotal = precio × cantidad con centavos; enlace con SITE_URL."""
        pedido = _crear_pedido_pagado(precio='99.50', cantidad=3)
        enviar_confirmacion_pedido.delay(pedido.pk)

        html = mail.outbox[0].alternatives[0][0]
        self.assertIn('$298.50', html)          # widthratio daría $298
        self.assertIn('https://erp-test.onrender.com/catalogo/', html)

    def test_texto_plano_no_escapa_html(self):
        """La versión .txt no debe mostrar entidades HTML (&#x27; / &amp;)."""
        pedido = _crear_pedido_pagado(nombre_cliente="O'Brien & Hijos")
        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertIn("O'Brien & Hijos", mail.outbox[0].body)

    def test_fallo_de_envio_no_marca_correo_enviado(self):
        """Si SendGrid falla, la tarea reintenta/propaga y NO marca el pedido."""
        pedido = _crear_pedido_pagado()
        with patch(
            'django.core.mail.EmailMultiAlternatives.send',
            side_effect=ConnectionError('SendGrid caído'),
        ):
            # En modo EAGER Celery reintenta y termina lanzando Retry
            with self.assertRaises((ConnectionError, Retry)):
                enviar_confirmacion_pedido.delay(pedido.pk)

        pedido.refresh_from_db()
        self.assertFalse(pedido.correo_enviado)


@override_settings(**EMAIL_SETTINGS)
class AlertaStockTest(TestCase):
    """Tests del correo de alerta de stock bajo."""

    def setUp(self):
        mail.outbox = []
        ConfiguracionERP.get_instance()

    def test_alerta_enviada_si_hay_stock_bajo(self):
        """Si hay productos con stock < umbral, se envía alerta al admin."""
        cat = Categoria.objects.create(nombre='Cat Alert')
        Producto.objects.create(
            nombre='Stock Bajo', precio=Decimal('50.00'),
            stock=2, categoria=cat
        )

        verificar_stock_bajo.delay(umbral=5)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('admin@test.com', mail.outbox[0].to)

    def test_alerta_contiene_nombre_producto(self):
        """El correo de alerta debe mencionar el producto con stock bajo."""
        cat = Categoria.objects.create(nombre='Cat Alert2')
        Producto.objects.create(
            nombre='Teclado Escaso', precio=Decimal('200.00'),
            stock=1, categoria=cat
        )

        verificar_stock_bajo.delay(umbral=5)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Teclado Escaso', mail.outbox[0].body)

    def test_no_alerta_si_todo_ok(self):
        """Si todos los productos tienen stock >= umbral, no se envía correo."""
        cat = Categoria.objects.create(nombre='Cat OK')
        Producto.objects.create(
            nombre='Bien surtido', precio=Decimal('100.00'),
            stock=20, categoria=cat
        )

        verificar_stock_bajo.delay(umbral=5)

        self.assertEqual(len(mail.outbox), 0)
