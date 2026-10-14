"""Suite de pruebas W03 — Archivos de despliegue y configuración.

Verifica la existencia y contenido mínimo de los artefactos
necesarios para desplegar en Render.com.

Ejecutar con:
    python manage.py test tests.test_w03_deploy --verbosity=2

Resultado esperado:
    Ran 10 tests in X.XXXs
    OK
"""
import os
from pathlib import Path

from django.conf import settings
from django.test import TestCase

# Ruta raíz del proyecto (donde está manage.py)
BASE_DIR = Path(settings.BASE_DIR)


class ArchivosDesplieguTest(TestCase):
    """Verifica que los archivos de despliegue existen en el repositorio."""

    def test_procfile_existe(self):
        """Procfile debe existir en la raíz del proyecto."""
        self.assertTrue(
            (BASE_DIR / 'Procfile').exists(),
            "Procfile no encontrado en la raíz del proyecto"
        )

    def test_procfile_contiene_gunicorn(self):
        """Procfile debe iniciar Gunicorn, no runserver."""
        procfile = BASE_DIR / 'Procfile'
        if procfile.exists():
            content = procfile.read_text(encoding='utf-8')
            self.assertIn(
                'gunicorn', content,
                "Procfile debe usar gunicorn, no python manage.py runserver"
            )

    def test_dockerfile_existe(self):
        """Dockerfile debe existir en la raíz del proyecto."""
        self.assertTrue(
            (BASE_DIR / 'Dockerfile').exists(),
            "Dockerfile no encontrado"
        )

    def test_render_yaml_existe(self):
        """render.yaml debe existir en la raíz del proyecto."""
        self.assertTrue(
            (BASE_DIR / 'render.yaml').exists(),
            "render.yaml no encontrado"
        )

    def test_docker_compose_existe(self):
        """docker-compose.yml debe existir en la raíz."""
        self.assertTrue(
            (BASE_DIR / 'docker-compose.yml').exists(),
            "docker-compose.yml no encontrado"
        )

    def test_ficha_schmelkes_e1_existe(self):
        """La ficha Schmelkes de la Espiral 1 debe existir."""
        self.assertTrue(
            (BASE_DIR / 'fichas' / 'espiral_01_infra.md').exists(),
            "fichas/espiral_01_infra.md no encontrado"
        )


class RequirementsProduccionTest(TestCase):
    """Verifica que requirements.txt incluye dependencias de producción."""

    def _leer_requirements(self):
        req_path = BASE_DIR / 'requirements.txt'
        if not req_path.exists():
            self.fail("requirements.txt no encontrado")
        return req_path.read_text(encoding='utf-8').lower()

    def test_gunicorn_en_requirements(self):
        """gunicorn debe estar en requirements.txt."""
        self.assertIn('gunicorn', self._leer_requirements(),
                      "gunicorn falta en requirements.txt")

    def test_psycopg2_en_requirements(self):
        """psycopg2-binary debe estar en requirements.txt."""
        self.assertIn('psycopg2', self._leer_requirements(),
                      "psycopg2-binary falta en requirements.txt")

    def test_dj_database_url_en_requirements(self):
        """dj-database-url debe estar en requirements.txt."""
        self.assertIn('dj-database-url', self._leer_requirements(),
                      "dj-database-url falta en requirements.txt")


class SettingsProdTest(TestCase):
    """Verifica el contenido de settings_prod.py leyendo el archivo."""

    def _leer_settings_prod(self):
        path = BASE_DIR / 'core' / 'settings_prod.py'
        if not path.exists():
            self.fail("core/settings_prod.py no encontrado")
        return path.read_text(encoding='utf-8')

    def test_settings_prod_tiene_debug_false(self):
        """settings_prod.py debe tener DEBUG = False."""
        content = self._leer_settings_prod()
        self.assertIn(
            'DEBUG = False', content,
            "settings_prod.py debe contener 'DEBUG = False'"
        )

    def test_settings_prod_importa_dj_database_url(self):
        """settings_prod.py debe importar dj_database_url."""
        content = self._leer_settings_prod()
        self.assertIn(
            'dj_database_url', content,
            "settings_prod.py debe importar dj_database_url"
        )