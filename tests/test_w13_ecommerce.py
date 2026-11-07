"""Suite de pruebas W13 — Catálogo público y carrito de compras.

Verifica: catálogo sin auth, filtros, ciclo completo del carrito.

Ejecutar con:
    python manage.py test tests.test_w13_ecommerce --verbosity=2

Resultado esperado:
    Ran 8 tests in X.XXXs
    OK
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from productos.models import Categoria, Producto


class CatalogoPublicoTest(TestCase):
    """Tests del catálogo público (sin autenticación)."""

    def setUp(self):
        cat        = Categoria.objects.create(nombre='Electrónica')
        self.prod1 = Producto.objects.create(
            nombre='Laptop',  precio=Decimal('10000.00'),
            stock=5, categoria=cat
        )
        self.prod2 = Producto.objects.create(
            nombre='Mouse', precio=Decimal('250.00'),
            stock=20, categoria=cat
        )
        Producto.objects.create(
            nombre='Producto Inactivo', precio=Decimal('100.00'),
            stock=5, categoria=cat, activo=False
        )

    def test_catalogo_accesible_sin_auth(self):
        """GET /catalogo/ sin login → 200 (catálogo es público)."""
        r = self.client.get(reverse('catalogo:catalogo'))
        self.assertEqual(r.status_code, 200)

    def test_catalogo_solo_muestra_activos(self):
        """El catálogo no debe mostrar productos inactivos."""
        r = self.client.get(reverse('catalogo:catalogo'))
        nombres = [p.nombre for p in r.context['productos']]
        self.assertIn('Laptop', nombres)
        self.assertNotIn('Producto Inactivo', nombres)

    def test_catalogo_filtro_por_nombre(self):
        """Filtrar por nombre 'lapt' → solo muestra Laptop."""
        r = self.client.get(
            reverse('catalogo:catalogo'), {'nombre': 'lapt'}
        )
        self.assertEqual(r.status_code, 200)
        nombres = [p.nombre for p in r.context['productos']]
        self.assertIn('Laptop', nombres)
        self.assertNotIn('Mouse', nombres)

    def test_catalogo_filtro_por_precio_max(self):
        """Filtrar precio_max=500 → solo muestra Mouse (250)."""
        r = self.client.get(
            reverse('catalogo:catalogo'), {'precio_max': 500}
        )
        nombres = [p.nombre for p in r.context['productos']]
        self.assertIn('Mouse', nombres)
        self.assertNotIn('Laptop', nombres)


class CarritoTest(TestCase):
    """Tests del carrito de compras en sesión."""

    def setUp(self):
        cat       = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(
            nombre='Teclado', precio=Decimal('350.00'),
            stock=10, categoria=cat
        )

    def test_carrito_vacio_al_inicio(self):
        """Un carrito nuevo debe estar vacío."""
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['items'], [])

    def test_agregar_producto_incrementa_carrito(self):
        """POST agregar → producto aparece en el carrito."""
        self.client.post(
            reverse('catalogo:agregar', args=[self.prod.pk]),
            {'cantidad': 2}
        )
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(len(r.context['items']), 1)
        self.assertEqual(r.context['items'][0]['cantidad'], 2)

    def test_agregar_mismo_producto_acumula_cantidad(self):
        """Agregar el mismo producto dos veces → suma las cantidades."""
        url = reverse('catalogo:agregar', args=[self.prod.pk])
        self.client.post(url, {'cantidad': 1})
        self.client.post(url, {'cantidad': 3})
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.context['items'][0]['cantidad'], 4)

    def test_carrito_calcula_total_correcto(self):
        """Total = cantidad × precio. 2 × 350 = 700."""
        self.client.post(
            reverse('catalogo:agregar', args=[self.prod.pk]),
            {'cantidad': 2}
 )
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.context['total'], Decimal('700.00'))

    def test_remover_producto_lo_elimina(self):
        """POST remover → producto desaparece del carrito."""
        self.client.post(
            reverse('catalogo:agregar', args=[self.prod.pk]),
            {'cantidad': 1}
        )
        self.client.post(
            reverse('catalogo:remover', args=[self.prod.pk])
        )
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.context['items'], [])