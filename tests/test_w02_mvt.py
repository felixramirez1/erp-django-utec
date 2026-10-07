"""Suite de pruebas W02 — Patrón MVT: templates, vistas y estáticos.

Ejecutar con:
    python manage.py test tests.test_w02_mvt --verbosity=2

Resultado esperado:
    Ran 12 tests in X.XXXs
    OK
"""
from django.test import TestCase
from django.urls import reverse


class TemplatesRenderTest(TestCase):
    """Verifica que las vistas usan render() y los templates correctos."""

    def test_bienvenida_usa_template_correcto(self):
        """La vista de inicio debe renderizar bienvenida.html."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bienvenida.html')

    def test_bienvenida_extiende_base(self):
        """La página de inicio debe extender base.html."""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')

    def test_productos_usa_template_correcto(self):
        """La vista de productos debe usar productos/index.html."""
        response = self.client.get(reverse('productos:inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/index.html')

    def test_clientes_usa_template_correcto(self):
        """La vista de clientes debe usar clientes/index.html."""
        response = self.client.get(reverse('clientes:inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/index.html')

    def test_proveedores_usa_template_correcto(self):
        """La vista de proveedores debe usar proveedores/index.html."""
        response = self.client.get(reverse('proveedores:inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proveedores/index.html')

    def test_ventas_usa_template_correcto(self):
        """La vista de ventas debe usar ventas/index.html."""
        response = self.client.get(reverse('ventas:inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ventas/index.html')

    def test_reportes_usa_template_correcto(self):
        """La vista de reportes debe usar reportes/index.html."""
        response = self.client.get(reverse('reportes:inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reportes/index.html')


class ContextoBienvenidaTest(TestCase):
    """Verifica el contexto de la vista de bienvenida."""

    def test_contexto_contiene_modulos(self):
        """La vista de inicio debe pasar 'modulos' en el contexto."""
        response = self.client.get('/')
        self.assertIn('modulos', response.context,
                      "El contexto debe incluir la lista 'modulos'")

    def test_contexto_tiene_seis_modulos(self):
        """El contexto debe contener exactamente 6 módulos."""
        response = self.client.get('/')
        modulos = response.context.get('modulos', [])
        self.assertEqual(
            len(modulos), 6,
            f"Se esperaban 6 módulos, se encontraron {len(modulos)}"
        )


class StaticFilesConfigTest(TestCase):
    """Verifica la configuración de archivos estáticos y WhiteNoise."""

    def test_static_url_es_slash_static(self):
        """STATIC_URL debe ser '/static/'."""
        from django.conf import settings
        self.assertEqual(settings.STATIC_URL, '/static/')

    def test_static_root_configurado(self):
        """STATIC_ROOT debe estar definido."""
        from django.conf import settings
        self.assertTrue(bool(settings.STATIC_ROOT),
                        "STATIC_ROOT no está configurado")

    def test_whitenoise_en_middleware(self):
        """WhiteNoise debe estar en MIDDLEWARE."""
        from django.conf import settings
        self.assertIn(
            'whitenoise.middleware.WhiteNoiseMiddleware',
            settings.MIDDLEWARE,
            "WhiteNoise no está en MIDDLEWARE"
        )

    def test_whitenoise_despues_de_security(self):
        """WhiteNoise debe ir DESPUÉS de SecurityMiddleware."""
        from django.conf import settings
        m = settings.MIDDLEWARE
        idx_sec  = m.index('django.middleware.security.SecurityMiddleware')
        idx_wn   = m.index('whitenoise.middleware.WhiteNoiseMiddleware')
        self.assertLess(idx_sec, idx_wn,
                        "SecurityMiddleware debe ir ANTES que WhiteNoise")
