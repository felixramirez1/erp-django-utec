"""Suite de pruebas W01 — Verificación del entorno ERP Django.

Ejecutar con:
    python manage.py test tests.test_w01_entorno --verbosity=2

Resultado esperado:
    Ran 8 tests in X.XXXs
    OK
"""
import sys
from django.test import TestCase
from django.urls import reverse, NoReverseMatch


class PythonVersionTest(TestCase):
    """Verifica que el intérprete sea Python 3.11+."""

    def test_python_mayor_igual_3(self):
        """Python major version debe ser 3."""
        self.assertEqual(sys.version_info.major, 3)

    def test_python_minor_igual_11(self):
        """Python minor version debe ser 11 o superior."""
        self.assertGreaterEqual(sys.version_info.minor, 11)


class DjangoVersionTest(TestCase):
    """Verifica que Django sea la versión 4.2 LTS."""

    def test_django_version_4_2(self):
        """Django debe ser exactamente la versión 4.2.x."""
        import django
        major, minor = django.VERSION[0], django.VERSION[1]
        self.assertEqual(major, 4, "Django major debe ser 4")
        self.assertEqual(minor, 2, "Django minor debe ser 2 (LTS)")


class VistasBienvenidaTest(TestCase):
    """Verifica que las vistas de bienvenida respondan correctamente."""

    def test_inicio_http_200(self):
        """La página de inicio debe devolver HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(
            response.status_code, 200,
            "La vista de inicio no devolvió HTTP 200"
        )

    def test_admin_login_accesible(self):
        """El panel de admin debe ser accesible sin autenticación."""
        response = self.client.get('/admin/login/')
        self.assertEqual(
            response.status_code, 200,
            "El admin no está accesible — verificar urls.py"
        )

    def test_productos_app_responde(self):
        """La app productos debe devolver HTTP 200."""
        response = self.client.get('/productos/')
        self.assertEqual(response.status_code, 200)

    def test_clientes_app_responde(self):
        """La app clientes debe devolver HTTP 200."""
        response = self.client.get('/clientes/')
        self.assertEqual(response.status_code, 200)

    def test_ventas_app_responde(self):
        """La app ventas debe devolver HTTP 200."""
        response = self.client.get('/ventas/')
        self.assertEqual(response.status_code, 200)


class ConfiguracionDjangoTest(TestCase):
    """Verifica la configuración de settings.py."""

    def test_installed_apps_contiene_erp_apps(self):
        """Las 5 apps del ERP deben estar en INSTALLED_APPS."""
        from django.conf import settings
        apps_requeridas = [
            'clientes', 'proveedores', 'productos', 'ventas', 'reportes'
        ]
        for app in apps_requeridas:
            self.assertIn(
                app, settings.INSTALLED_APPS,
                f"La app '{app}' no está en INSTALLED_APPS"
            )

    def test_language_code_es_mx(self):
        """El idioma debe configurarse en español mexicano."""
        from django.conf import settings
        self.assertEqual(settings.LANGUAGE_CODE, 'es-mx')

    def test_media_root_configurado(self):
        """MEDIA_ROOT debe estar configurado."""
        from django.conf import settings
        self.assertTrue(
            bool(settings.MEDIA_ROOT),
            "MEDIA_ROOT no está configurado en settings.py"
        )
