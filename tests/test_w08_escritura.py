"""Suite de pruebas W08 — Vistas de escritura: Create, Update, Delete.

Verifica: redirección sin auth, GET con auth, POST válido,
          POST inválido, borrado con redirect.

Ejecutar con:
    python manage.py test tests.test_w08_escritura --verbosity=2

Resultado esperado:
    Ran 12 tests in X.XXXs
    OK
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from clientes.models    import Cliente
from productos.models   import Categoria, Producto
from proveedores.models import Proveedor
from ventas.models      import Venta


class ProductoEscrituraTest(TestCase):
    """Tests de CreateView, UpdateView y DeleteView de Producto."""

    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', password='testpass123'
        )
        self.cat  = Categoria.objects.create(nombre='Cat Test')
        self.prod = Producto.objects.create(
            nombre='Laptop', precio=Decimal('10000.00'),
            stock=5, categoria=self.cat
        )

    # ── Protección de autenticación ──────────────────────────────────────

    def test_crear_sin_auth_redirige_a_login(self):
        """GET /productos/nuevo/ sin login → 302 a /accounts/login/."""
        r = self.client.get(reverse('productos:crear'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_editar_sin_auth_redirige_a_login(self):
        """GET /productos/<id>/editar/ sin login → 302."""
        r = self.client.get(
            reverse('productos:editar', args=[self.prod.pk])
        )
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    # ── Vistas con autenticación ─────────────────────────────────────────

    def test_crear_con_auth_http_200(self):
        """GET /productos/nuevo/ con login → 200."""
        self.client.force_login(self.user)
        r = self.client.get(reverse('productos:crear'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'productos/crear.html')

    def test_post_valido_crea_producto(self):
        """POST con datos válidos crea el producto y redirige a la lista."""
        self.client.force_login(self.user)
        datos = {
            'nombre':    'Monitor 4K',
            'precio':    '5500.00',
            'stock':     '3',
            'categoria': self.cat.pk,
            'activo':    True,
        }
        r = self.client.post(reverse('productos:crear'), datos)
        self.assertRedirects(r, reverse('productos:lista'))
        self.assertTrue(
            Producto.objects.filter(nombre='Monitor 4K').exists()
        )

    def test_post_invalido_muestra_errores(self):
        """POST con precio negativo → 200 con errores en el formulario."""
        self.client.force_login(self.user)
        datos = {
            'nombre':    'Producto mal',
            'precio':    '-100.00',   # inválido
            'stock':     '5',
            'categoria': self.cat.pk,
        }
        r = self.client.post(reverse('productos:crear'), datos)
        self.assertEqual(r.status_code, 200)
        self.assertFormError(r, 'form', 'precio',
                             'Ensure this value is greater than or equal to 0.00.')

    def test_delete_elimina_producto(self):
        """POST /productos/<id>/eliminar/ → borra el producto y redirige."""
        self.client.force_login(self.user)
        pk = self.prod.pk
        r  = self.client.post(
            reverse('productos:eliminar', args=[pk])
        )
        self.assertRedirects(r, reverse('productos:lista'))
        self.assertFalse(Producto.objects.filter(pk=pk).exists())


class ClienteEscrituraTest(TestCase):
    """Tests de CreateView de Cliente."""

    def setUp(self):
        self.user = User.objects.create_user('userC', password='pass')

    def test_crear_cliente_sin_auth_redirige(self):
        r = self.client.get(reverse('clientes:crear'))
        self.assertEqual(r.status_code, 302)

    def test_post_valido_crea_cliente(self):
        """POST válido crea el cliente y redirige."""
        self.client.force_login(self.user)
        r = self.client.post(reverse('clientes:crear'), {
            'nombre': 'María López',
            'correo': 'maria@test.com',
            'activo': True,
        })
        self.assertRedirects(r, reverse('clientes:lista'))
        self.assertTrue(
            Cliente.objects.filter(correo='maria@test.com').exists()
        )

    def test_post_correo_duplicado_muestra_error(self):
        """POST con correo ya existente → 200 con error de unicidad."""
        Cliente.objects.create(nombre='Ana', correo='dup@test.com')
        self.client.force_login(self.user)
        r = self.client.post(reverse('clientes:crear'), {
            'nombre': 'Otro',
            'correo': 'dup@test.com',
            'activo': True,
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'ya existe')


class ProveedorEscrituraTest(TestCase):
    """Tests de CreateView y DeleteView de Proveedor."""

    def setUp(self):
        self.user = User.objects.create_user('userP', password='pass')
        self.prov = Proveedor.objects.create(
            nombre='Prov Test', correo='prov@test.com'
        )

    def test_crear_proveedor_sin_auth_redirige(self):
        r = self.client.get(reverse('proveedores:crear'))
        self.assertEqual(r.status_code, 302)

    def test_delete_proveedor_con_auth(self):
        """POST /proveedores/<id>/eliminar/ → borra y redirige."""
        self.client.force_login(self.user)
        pk = self.prov.pk
        r  = self.client.post(
            reverse('proveedores:eliminar', args=[pk])
        )
        self.assertRedirects(r, reverse('proveedores:lista'))
        self.assertFalse(Proveedor.objects.filter(pk=pk).exists())


class VentaEscrituraTest(TestCase):
    """Tests de crear_venta y VentaDeleteView."""

    def setUp(self):
        self.user = User.objects.create_user('userV', password='pass')
        cat       = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(
            nombre='P', precio=Decimal('100.00'), stock=5, categoria=cat
        )
        self.cli  = Cliente.objects.create(nombre='C', correo='c@t.com')

    def test_crear_venta_sin_auth_redirige(self):
        r = self.client.get(reverse('ventas:crear'))
        self.assertEqual(r.status_code, 302)

    def test_post_valido_crea_venta(self):
        """POST válido crea Venta + DetalleVenta y redirige al detalle."""
        self.client.force_login(self.user)
        r = self.client.post(reverse('ventas:crear'), {
            'cliente':         self.cli.pk,
            'producto':        self.prod.pk,
            'cantidad':        2,
            'precio_unitario': '100.00',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Venta.objects.count(), 1)
        venta = Venta.objects.first()
        self.assertEqual(venta.total, Decimal('200.00'))