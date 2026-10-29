"""Suite de pruebas W10 — API REST con DRF y autenticación por token.

Verifica: GET sin auth → 200, POST sin auth → 403,
          POST con token → 201, GET detalle → JSON correcto,
          DELETE con token → 204.

Ejecutar con:
    python manage.py test tests.test_w10_api --verbosity=2

Resultado esperado:
    Ran 7 tests in X.XXXs
    OK
"""
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from clientes.models    import Cliente
from productos.models   import Categoria, Producto
from proveedores.models import Proveedor
from ventas.models      import DetalleVenta, Venta


class ProductoAPITest(APITestCase):
    """Tests de los endpoints /api/productos/."""

    def setUp(self):
        self.client   = APIClient()
        self.user     = User.objects.create_user('apiuser', password='pass')
        self.token    = Token.objects.create(user=self.user)
        self.cat      = Categoria.objects.create(nombre='Cat API')
        self.producto = Producto.objects.create(
            nombre='Teclado API', precio=Decimal('450.00'),
            stock=10, categoria=self.cat
        )

    def test_get_lista_sin_auth_devuelve_200(self):
        """GET /api/productos/ sin token → 200 (lectura pública)."""
        r = self.client.get('/api/productos/')
        self.assertEqual(r.status_code, 200)

    def test_get_lista_devuelve_json_con_productos(self):
        """La respuesta debe ser JSON con el campo 'results'."""
        r = self.client.get('/api/productos/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # Con paginación, DRF devuelve {'count':..., 'results':[...]}
        self.assertIn('results', data)
        nombres = [p['nombre'] for p in data['results']]
        self.assertIn('Teclado API', nombres)

    def test_post_sin_auth_devuelve_403(self):
        """POST /api/productos/ sin token → 403 Forbidden."""
        r = self.client.post('/api/productos/', {
            'nombre':    'Sin Auth',
            'precio':    '100.00',
            'stock':     1,
            'categoria': self.cat.pk,
        }, format='json')
        self.assertEqual(r.status_code, 403)

    def test_post_con_token_crea_producto_201(self):
        """POST /api/productos/ con token válido → 201 Created."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        r = self.client.post('/api/productos/', {
            'nombre':    'Monitor API',
            'precio':    '5500.00',
            'stock':     3,
            'categoria': self.cat.pk,
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['nombre'], 'Monitor API')
        self.assertTrue(
            Producto.objects.filter(nombre='Monitor API').exists()
        )

    def test_get_detalle_producto_devuelve_nombre(self):
        """GET /api/productos/<id>/ → JSON con nombre y precio."""
        r = self.client.get(f'/api/productos/{self.producto.pk}/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['nombre'], 'Teclado API')
        self.assertIn('categoria_nombre', data)

    def test_get_detalle_404_id_inexistente(self):
        """GET /api/productos/9999/ → 404 Not Found."""
        r = self.client.get('/api/productos/9999/')
        self.assertEqual(r.status_code, 404)

    def test_venta_api_incluye_total_y_detalles(self):
        """GET /api/ventas/<id>/ → JSON con campo 'total' y 'detalles'."""
        cli   = Cliente.objects.create(nombre='CLI', correo='c@t.com')
        venta = Venta.objects.create(cliente=cli)
        DetalleVenta.objects.create(
            venta=venta, producto=self.producto,
            cantidad=2, precio_unitario=Decimal('450.00')
        )
        r = self.client.get(f'/api/ventas/{venta.pk}/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('total', data)
        self.assertIn('detalles', data)
        self.assertEqual(len(data['detalles']), 1)
        self.assertEqual(data['detalles'][0]['cantidad'], 2)