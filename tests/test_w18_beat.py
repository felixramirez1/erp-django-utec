"""Suite de pruebas W18 — Celery Beat y tarea de reporte diario.

Verifica la configuración del schedule, la ejecución de la tarea
y el envío del correo de reporte.

Ejecutar con:
    python manage.py test tests.test_w18_beat --verbosity=2

Resultado esperado:
    Ran 8 tests in X.XXXs
    OK
"""
from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from clientes.models      import Cliente
from configuracion.models import ConfiguracionERP
from productos.models     import Categoria, Producto
from ventas.models        import DetalleVenta, Pedido, Venta
from ventas.tasks         import reporte_ventas_diario, verificar_stock_bajo

EMAIL_SETTINGS = {
    'EMAIL_BACKEND':               'django.core.mail.backends.locmem.EmailBackend',
    'CELERY_TASK_ALWAYS_EAGER':    True,
    'CELERY_TASK_EAGER_PROPAGATES': True,
    'ADMINS':           [('Admin Test', 'admin@test.com')],
    'DEFAULT_FROM_EMAIL': 'test@erp.com',
}


class BeatScheduleConfigTest(TestCase):
    """Verifica la configuración de CELERY_BEAT_SCHEDULE."""

    def test_beat_schedule_tiene_verificar_stock(self):
        """El schedule debe incluir verificar_stock_bajo."""
        schedule = settings.CELERY_BEAT_SCHEDULE
        tareas   = [v['task'] for v in schedule.values()]
        self.assertIn('ventas.verificar_stock_bajo', tareas)

    def test_beat_schedule_tiene_reporte_diario(self):
        """El schedule debe incluir reporte_ventas_diario."""
        schedule = settings.CELERY_BEAT_SCHEDULE
        tareas   = [v['task'] for v in schedule.values()]
        self.assertIn('ventas.reporte_ventas_diario', tareas)

    def test_reporte_usa_crontab(self):
        """El reporte diario debe usar crontab (no timedelta)."""
        from celery.schedules import crontab
        schedule = settings.CELERY_BEAT_SCHEDULE
        for nombre, config in schedule.items():
            if config['task'] == 'ventas.reporte_ventas_diario':
                self.assertIsInstance(
                    config['schedule'], crontab,
                    "reporte_ventas_diario debe usar crontab, no timedelta"
                )
                break

    def test_verificar_stock_usa_timedelta(self):
        """verificar_stock_bajo debe usar timedelta (intervalo)."""
        schedule = settings.CELERY_BEAT_SCHEDULE
        for nombre, config in schedule.items():
            if config['task'] == 'ventas.verificar_stock_bajo':
                self.assertIsInstance(
                    config['schedule'], timedelta,
                    "verificar_stock_bajo debe usar timedelta"
                )
                break


@override_settings(**EMAIL_SETTINGS)
class ReporteVentasTest(TestCase):
    """Tests de la tarea reporte_ventas_diario."""

    def setUp(self):
        mail.outbox = []
        ConfiguracionERP.get_instance()
        cat      = Categoria.objects.create(nombre='Cat Rep')
        self.prod = Producto.objects.create(
            nombre='Producto Reporte', precio=Decimal('500.00'),
            stock=10, categoria=cat
        )
        cli        = Cliente.objects.create(
            nombre='Cliente Rep', correo='rep@test.com'
        )
        # Crear una venta de HOY
        venta = Venta.objects.create(cliente=cli)
        DetalleVenta.objects.create(
            venta=venta, producto=self.prod,
            cantidad=3, precio_unitario=Decimal('500.00')
        )
        # Crear un pedido pagado de HOY
        Pedido.objects.create(
            numero_pedido = 'PED-REP-001',
            cliente       = cli,
            estado        = 'pagado',
            total_pagado  = Decimal('1500.00'),
        )

    def test_reporte_envia_correo_al_admin(self):
        """La tarea debe enviar correo al administrador."""
        reporte_ventas_diario.delay()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('admin@test.com', mail.outbox[0].to)

    def test_reporte_asunto_contiene_fecha(self):
        """El asunto debe contener la fecha del reporte."""
        reporte_ventas_diario.delay()
        fecha_str = timezone.localdate().strftime('%d/%m/%Y')
        self.assertIn(fecha_str, mail.outbox[0].subject)

    def test_reporte_sin_ventas_hoy_envia_correo(self):
        """Aunque no haya ventas, el reporte debe enviarse."""
        # Eliminar ventas y pedidos creados en setUp
        Pedido.objects.all().delete()
        DetalleVenta.objects.all().delete()

        reporte_ventas_diario.delay()

        self.assertEqual(len(mail.outbox), 1)
        # Verificar que menciona 0 pedidos en el texto plano
        cuerpo = mail.outbox[0].body
        self.assertIn('0', cuerpo)

    def test_reporte_devuelve_dict_con_totales(self):
        """La tarea debe devolver un dict con total_pedidos y facturado."""
        resultado = reporte_ventas_diario.delay().get()
        self.assertIn('total_pedidos',   resultado)
        self.assertIn('total_facturado', resultado)
        self.assertIn('top_productos',   resultado)
        self.assertGreaterEqual(resultado['total_pedidos'], 0)


# ── Regresión (2026-11-20): compras en línea y hora configurable ─────────

@override_settings(**EMAIL_SETTINGS)
class ReporteTiendaEnLineaTest(TestCase):
    """El checkout solo crea Pedido (no Venta): el top debe incluirlo."""

    def setUp(self):
        mail.outbox = []
        ConfiguracionERP.get_instance()
        cli = Cliente.objects.create(nombre='Cliente Web', correo='web@test.com')
        Pedido.objects.create(
            numero_pedido  = 'PED-WEB-001',
            cliente        = cli,
            estado         = 'pagado',
            total_pagado   = Decimal('231.42'),
            items_snapshot = [
                {'producto_id': 1, 'nombre': 'Vino Web',
                 'cantidad': 2, 'precio': '99.75'},
            ],
        )

    def test_top_incluye_productos_de_pedidos_en_linea(self):
        resultado = reporte_ventas_diario.delay().get()
        self.assertEqual(resultado['total_pedidos'], 1)
        self.assertEqual(
            resultado['top_productos'],
            [{'nombre': 'Vino Web', 'unidades': 2, 'ingreso': '199.50'}],
        )
        self.assertIn('Vino Web', mail.outbox[0].body)


class HoraReporteConfigurableTest(TestCase):
    """La hora del crontab sale de REPORTE_DIARIO_HORA (hora de México)."""

    def test_crontab_coincide_con_reporte_diario_hora(self):
        h, m = (int(x) for x in settings.REPORTE_DIARIO_HORA.split(':'))
        cron = settings.CELERY_BEAT_SCHEDULE['reporte-ventas-diario-8am']['schedule']
        self.assertEqual(cron.hour, {h})
        self.assertEqual(cron.minute, {m})
        self.assertEqual(settings.CELERY_TIMEZONE, 'America/Mexico_City')
