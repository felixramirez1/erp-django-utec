
"""Suite de pruebas W04 — Artefactos de diseño del modelo ER.

Verifica que los documentos de diseño existen y tienen contenido mínimo.
No se prueban modelos Django (aún no existen — eso es W05).

Ejecutar con:
    python manage.py test tests.test_w04_diseno --verbosity=2

Resultado esperado:
    Ran 8 tests in X.XXXs
    OK
"""
from pathlib import Path

from django.conf import settings
from django.test import TestCase

BASE_DIR = Path(settings.BASE_DIR)


class DocumentosDisenioTest(TestCase):
    """Verifica existencia de artefactos de diseño del ER."""

    def test_docs_diagrama_er_existe(self):
        """El diagrama ER en Mermaid debe existir."""
        self.assertTrue(
            (BASE_DIR / 'docs' / 'diagramas' / 'diagrama_er.md').exists(),
            "docs/diagramas/diagrama_er.md no encontrado"
        )

    def test_diagrama_er_contiene_mermaid(self):
        """El diagrama ER debe contener bloques Mermaid."""
        path = BASE_DIR / 'docs' / 'diagramas' / 'diagrama_er.md'
        if path.exists():
            content = path.read_text(encoding='utf-8')
            self.assertIn('mermaid', content.lower(),
                          "diagrama_er.md no contiene bloque Mermaid")

    def test_diagrama_er_contiene_entidades_clave(self):
        """El diagrama debe mencionar las 8 entidades del ERP."""
        path = BASE_DIR / 'docs' / 'diagramas' / 'diagrama_er.md'
        if path.exists():
            content = path.read_text(encoding='utf-8').upper()
            for entidad in ['CLIENTE', 'PRODUCTO', 'VENTA', 'PROVEEDOR',
                            'CATEGORIA', 'DETALLE_VENTA']:
                self.assertIn(
                    entidad, content,
                    f"Entidad '{entidad}' no encontrada en el diagrama ER"
                )

    def test_entidades_atributos_existe(self):
        """El documento de entidades y atributos debe existir."""
        self.assertTrue(
            (BASE_DIR / 'docs' / 'entidades_atributos.md').exists(),
            "docs/entidades_atributos.md no encontrado"
        )

    def test_decisiones_diseno_existe(self):
        """El documento de decisiones de diseño debe existir."""
        self.assertTrue(
            (BASE_DIR / 'docs' / 'decisiones_diseno.md').exists(),
            "docs/decisiones_diseno.md no encontrado"
        )

    def test_decisiones_diseno_tiene_contenido(self):
        """El documento de decisiones debe tener al menos 5 decisiones."""
        path = BASE_DIR / 'docs' / 'decisiones_diseno.md'
        if path.exists():
            content = path.read_text(encoding='utf-8')
            # Contamos encabezados de decisión (### D-0N)
            decisiones = [l for l in content.splitlines()
                          if l.startswith('### D-')]
            self.assertGreaterEqual(
                len(decisiones), 5,
                f"Se esperaban ≥ 5 decisiones documentadas, "
                f"se encontraron {len(decisiones)}"
            )

    def test_sprint1_planning_existe(self):
        """El Sprint 1 Planning debe existir."""
        self.assertTrue(
            (BASE_DIR / 'sprint1_planning.md').exists(),
            "sprint1_planning.md no encontrado"
        )

    def test_sprint1_planning_tiene_sprint_goal(self):
        """El Sprint 1 Planning debe contener el Sprint Goal."""
        path = BASE_DIR / 'sprint1_planning.md'
        if path.exists():
            content = path.read_text(encoding='utf-8')
            self.assertIn(
                'Sprint Goal', content,
                "sprint1_planning.md debe contener 'Sprint Goal'"
            )
