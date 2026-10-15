"""Suite de pruebas W05 — Smoke tests de modelos Django.

Verifica que los 8 modelos pueden crearse y sus métodos básicos
funcionan correctamente. La suite completa con validators y
casos borde se implementa en W06 (≥ 15 tests).

Ejecutar con:
    python manage.py test tests.test_w05_modelos --verbosity=2

Resultado esperado:
    Ran 10 tests in X.XXXs
    OK
"""
from decimal import Decimal

from django.test import TestCase

from clientes.models       import Cliente
from configuracion.models  import ConfiguracionERP
from productos.models      import Categoria, Producto
from proveedores.models    import Proveedor
from ventas.models         import DetalleVenta, Pedido, Venta


class ClienteModelTest(TestCase):
    """Smoke tests del modelo Cliente."""

    def test_cliente_puede_crearse(self):
        """Un cliente con datos válidos debe guardarse sin errores."""
        c = Cliente.objects.create(nombre='Ana Pérez', correo='ana@test.com')
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(c.nombre, 'Ana Pérez')

    def test_str_cliente(self):
        """__str__ de Cliente debe devolver el nombre."""
        c = Cliente(nombre='Luis García', correo='luis@test.com')
        self.assertEqual(str(c), 'Luis García')

    def test_cliente_activo_por_defecto(self):
        """Un cliente nuevo debe estar activo por defecto."""
        c = Cliente.objects.create(nombre='X', correo='x@test.com')
        self.assertTrue(c.activo)


class ProductoModelTest(TestCase):
    """Smoke tests del modelo Producto."""

    def setUp(self):
        self.cat  = Categoria.objects.create(nombre='Electrónica')
        self.prov = Proveedor.objects.create(
            nombre='Dist. Tech', correo='dist@tech.com'
        )

    def test_producto_puede_crearse(self):
        """Un producto con FK válidas debe guardarse sin errores."""
        p = Producto.objects.create(
            nombre='Laptop', precio=Decimal('12500.00'),
            stock=5, categoria=self.cat
        )
        self.assertEqual(p.nombre, 'Laptop')
        self.assertIsNone(p.proveedor)   # proveedor es opcional

    def test_str_producto_formato_correcto(self):
        """__str__ de Producto debe mostrar nombre y precio formateado."""
        p = Producto(nombre='Mouse', precio=Decimal('250.00'),
                     stock=10, categoria=self.cat)
        self.assertEqual(str(p), 'Mouse ($250.00)')

    def test_producto_sin_proveedor_es_valido(self):
        """Producto puede existir sin proveedor (D-02)."""
        p = Producto.objects.create(
            nombre='Interno', precio=Decimal('100.00'),
            stock=1, categoria=self.cat, proveedor=None
        )
        self.assertIsNone(p.proveedor)


class VentaModelTest(TestCase):
    """Smoke tests del modelo Venta y su propiedad total."""

    def setUp(self):
        cat       = Categoria.objects.create(nombre='General')
        self.prod = Producto.objects.create(
            nombre='Teclado', precio=Decimal('350.00'),
            stock=10, categoria=cat
        )
        self.cli  = Cliente.objects.create(
            nombre='Juan', correo='juan@test.com'
        )
        self.venta = Venta.objects.create(cliente=self.cli)

    def test_venta_puede_crearse(self):
        """Una venta con cliente válido debe guardarse."""
        self.assertEqual(Venta.objects.count(), 1)

    def test_venta_total_sin_detalles_es_cero(self):
        """Una venta sin líneas debe tener total = 0."""
        self.assertEqual(self.venta.total, Decimal('0.00'))

    def test_detalle_venta_subtotal(self):
        """Subtotal = cantidad × precio_unitario."""
        d = DetalleVenta.objects.create(
            venta=self.venta, producto=self.prod,
            cantidad=3, precio_unitario=Decimal('350.00')
        )
        self.assertEqual(d.subtotal, Decimal('1050.00'))

    def test_venta_total_con_detalles(self):
        """Total de la venta = suma de subtotales de sus líneas (D-04)."""
        DetalleVenta.objects.create(
            venta=self.venta, producto=self.prod,
            cantidad=2, precio_unitario=Decimal('350.00')
        )
        self.assertEqual(self.venta.total, Decimal('700.00'))


class ConfiguracionERPTest(TestCase):
    """Smoke tests del modelo singleton ConfiguracionERP."""

    def test_get_instance_crea_registro(self):
        """get_instance() debe crear el registro con pk=1."""
        cfg = ConfiguracionERP.get_instance()
        self.assertEqual(cfg.pk, 1)

    def test_get_instance_es_singleton(self):
        """Dos llamadas a get_instance() deben devolver el mismo registro."""
        cfg1 = ConfiguracionERP.get_instance()
        cfg2 = ConfiguracionERP.get_instance()
        self.assertEqual(cfg1.pk, cfg2.pk)
        self.assertEqual(ConfiguracionERP.objects.count(), 1)