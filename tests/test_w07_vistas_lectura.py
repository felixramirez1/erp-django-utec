"""Suite de pruebas W07 — Vistas de lectura: ListView y DetailView.

Verifica: HTTP 200, templates correctos, contexto con objetos,
          paginación y 404 para IDs inexistentes.

Ejecutar con:
    python manage.py test tests.test_w07_vistas_lectura --verbosity=2

Resultado esperado:
    Ran 12 tests in X.XXXs
    OK
"""
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from clientes.models    import Cliente
from productos.models   import Categoria, Producto
from proveedores.models import Proveedor
from ventas.models      import DetalleVenta, Venta


class ProductoVistaTest(TestCase):
    """Tests de ListView y DetailView de Producto."""

    def setUp(self):
        self.cat  = Categoria.objects.create(nombre='Cat Test')
        self.prod = Producto.objects.create(
            nombre='Laptop Test', precio=Decimal('10000.00'),
            stock=5, categoria=self.cat
        )

    def test_lista_productos_http_200(self):
        """GET /productos/ debe devolver HTTP 200."""
        r = self.client.get(reverse('productos:lista'))
        self.assertEqual(r.status_code, 200)

    def test_lista_productos_usa_template_correcto(self):
        """GET /productos/ debe renderizar productos/lista.html."""
        r = self.client.get(reverse('productos:lista'))
        self.assertTemplateUsed(r, 'productos/lista.html')

    def test_lista_muestra_producto_en_contexto(self):
        """El contexto de la lista debe contener el producto creado."""
        r = self.client.get(reverse('productos:lista'))
        self.assertIn('productos', r.context)
        self.assertContains(r, 'Laptop Test')

    def test_detalle_producto_http_200(self):
        """GET /productos/<id>/ debe devolver HTTP 200."""
        r = self.client.get(
            reverse('productos:detalle', args=[self.prod.pk])
        )
        self.assertEqual(r.status_code, 200)

    def test_detalle_producto_404_id_inexistente(self):
        """GET /productos/9999/ debe devolver HTTP 404."""
        r = self.client.get(
            reverse('productos:detalle', args=[9999])
        )
        self.assertEqual(r.status_code, 404)

    def test_lista_paginacion_20_por_pagina(self):
        """Con 25 productos, la página 1 debe mostrar máximo 20."""
        for i in range(24):   # ya existe 1 del setUp → total 25
            Producto.objects.create(
                nombre=f'Prod {i}', precio=Decimal('10.00'),
                stock=1, categoria=self.cat
            )
        r = self.client.get(reverse('productos:lista'))
        self.assertEqual(len(r.context['productos']), 20)
        self.assertTrue(r.context['is_paginated'])


class ClienteVistaTest(TestCase):
    """Tests de ListView y DetailView de Cliente."""

    def setUp(self):
        self.cli = Cliente.objects.create(
            nombre='Ana García', correo='ana@test.com'
        )

    def test_lista_clientes_http_200(self):
        r = self.client.get(reverse('clientes:lista'))
        self.assertEqual(r.status_code, 200)

    def test_lista_clientes_template_correcto(self):
        r = self.client.get(reverse('clientes:lista'))
        self.assertTemplateUsed(r, 'clientes/lista.html')

    def test_detalle_cliente_contiene_nombre(self):
        """El detalle debe mostrar el nombre del cliente."""
        r = self.client.get(
            reverse('clientes:detalle', args=[self.cli.pk])
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Ana García')


class ProveedorVistaTest(TestCase):
    """Tests de ListView de Proveedor."""

    def setUp(self):
        self.prov = Proveedor.objects.create(
            nombre='Dist. Norte', correo='norte@dist.com'
        )

    def test_lista_proveedores_http_200(self):
        r = self.client.get(reverse('proveedores:lista'))
        self.assertEqual(r.status_code, 200)

    def test_detalle_proveedor_http_200(self):
        r = self.client.get(
            reverse('proveedores:detalle', args=[self.prov.pk])
        )
        self.assertEqual(r.status_code, 200)


class VentaVistaTest(TestCase):
    """Tests de ListView y DetailView de Venta."""

    def setUp(self):
        cat   = Categoria.objects.create(nombre='Cat')
        prod  = Producto.objects.create(
            nombre='P', precio=Decimal('100.00'),
            stock=5, categoria=cat
        )
        cli   = Cliente.objects.create(nombre='C', correo='c@t.com')
        self.venta = Venta.objects.create(cliente=cli)
        DetalleVenta.objects.create(
            venta=self.venta, producto=prod,
            cantidad=2, precio_unitario=Decimal('100.00')
        )

    def test_lista_ventas_http_200(self):
        r = self.client.get(reverse('ventas:lista'))
        self.assertEqual(r.status_code, 200)

    def test_detalle_venta_muestra_total(self):
        """El detalle de venta debe mostrar el total calculado."""
        r = self.client.get(
            reverse('ventas:detalle', args=[self.venta.pk])
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '200.00')   # total = 2 × 100