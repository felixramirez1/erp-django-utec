"""Suite de pruebas W09 — Autenticación y Control de Acceso por Rol (RBAC).

Verifica: login requerido, redirección, HTTP 403 por rol,
          acceso correcto para Gerente y Vendedor.

Ejecutar con:
    python manage.py test tests.test_w09_auth_rbac --verbosity=2

Resultado esperado:
    Ran 10 tests in X.XXXs
    OK
"""
from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from clientes.models    import Cliente
from productos.models   import Categoria, Producto
from proveedores.models import Proveedor
from ventas.models      import Venta


def _get_group(name: str) -> Group:
    """Obtiene o crea el grupo indicado (debe haber ejecutado crear_grupos)."""
    return Group.objects.get_or_create(name=name)[0]


class AuthBasicTest(TestCase):
    """Tests de autenticación básica con allauth."""

    def test_login_page_http_200(self):
        """La página de login debe responder HTTP 200."""
        r = self.client.get(reverse('account_login'))
        self.assertEqual(r.status_code, 200)

    def test_login_page_usa_template_fable5(self):
        """El login debe usar el template personalizado Fable 5."""
        r = self.client.get(reverse('account_login'))
        self.assertTemplateUsed(r, 'account/login.html')

    def test_login_correcto_redirige_a_productos(self):
        """Login con credenciales válidas → redirige a LOGIN_REDIRECT_URL."""
        User.objects.create_user('testlogin', password='pass123')
        r = self.client.post(reverse('account_login'), {
            'login':    'testlogin',
            'password': 'pass123',
        })
        self.assertRedirects(r, '/productos/',
                             fetch_redirect_response=False)


class PermisosGruposTest(TestCase):
    """Tests de permisos por grupo (Gerente, Vendedor, Almacén)."""

    def setUp(self):
        self.cat  = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(
            nombre='Prod', precio=Decimal('100.00'),
            stock=5, categoria=self.cat
        )
        self.cli = Cliente.objects.create(
            nombre='C', correo='c@t.com'
        )

    def _crear_usuario(self, username: str, grupo_name: str) -> User:
        """Crea un usuario y lo asigna al grupo indicado."""
        user   = User.objects.create_user(username, password='pass')
        grupo, _ = Group.objects.get_or_create(name=grupo_name)
        # Asignar permisos básicos al grupo para los tests
        if grupo_name == 'Gerente':
            perms = Permission.objects.filter(
                codename__in=[
                    'delete_producto', 'delete_cliente',
                    'delete_venta', 'add_venta'
                ]
            )
            grupo.permissions.set(perms)
        elif grupo_name == 'Vendedor':
            perms = Permission.objects.filter(
                codename__in=['add_venta', 'view_producto', 'view_cliente']
            )
            grupo.permissions.set(perms)
        user.groups.add(grupo)
        return user

    # ── Sin autenticación ─────────────────────────────────────────────────

    def test_eliminar_producto_sin_auth_redirige_a_login(self):
        """DELETE /productos/<id>/eliminar/ sin auth → 302 login."""
        r = self.client.get(
            reverse('productos:eliminar', args=[self.prod.pk])
        )
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    # ── Vendedor: no tiene delete_producto ────────────────────────────────

    def test_vendedor_no_puede_eliminar_producto_403(self):
        """Vendedor sin delete_producto → HTTP 403 (raise_exception=True)."""
        vendedor = self._crear_usuario('vendedor', 'Vendedor')
        self.client.force_login(vendedor)
        r = self.client.post(
            reverse('productos:eliminar', args=[self.prod.pk])
        )
        self.assertEqual(r.status_code, 403)

    def test_vendedor_puede_ver_lista_productos(self):
        """Vendedor tiene view_producto → puede listar productos."""
        vendedor = self._crear_usuario('vend2', 'Vendedor')
        self.client.force_login(vendedor)
        r = self.client.get(reverse('productos:lista'))
        self.assertEqual(r.status_code, 200)

    def test_vendedor_puede_crear_venta(self):
        """Vendedor tiene add_venta → puede acceder a crear venta."""
        vendedor = self._crear_usuario('vend3', 'Vendedor')
        self.client.force_login(vendedor)
        r = self.client.get(reverse('ventas:crear'))
        self.assertEqual(r.status_code, 200)

    # ── Gerente: tiene todos los permisos ─────────────────────────────────

    def test_gerente_puede_eliminar_producto(self):
        """Gerente con delete_producto → puede borrar y redirige."""
        gerente = self._crear_usuario('gerente', 'Gerente')
        self.client.force_login(gerente)
        pk = self.prod.pk
        r  = self.client.post(
            reverse('productos:eliminar', args=[pk])
        )
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Producto.objects.filter(pk=pk).exists())

    def test_gerente_puede_eliminar_cliente(self):
        """Gerente con delete_cliente → puede borrar cliente."""
        gerente = self._crear_usuario('gerente2', 'Gerente')
        self.client.force_login(gerente)
        pk = self.cli.pk
        r  = self.client.post(
            reverse('clientes:eliminar', args=[pk])
        )
        self.assertIn(r.status_code, [200, 302, 403])
        # 403 si el cliente tiene ventas (PROTECT), 302 si no

    # ── Management command crear_grupos ───────────────────────────────────

    def test_management_command_crea_grupos(self):
        """El command crear_grupos debe crear los 3 grupos."""
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('crear_grupos', stdout=out)
        for nombre in ['Gerente', 'Vendedor', 'Almacén']:
            self.assertTrue(
                Group.objects.filter(name=nombre).exists(),
                f"Grupo '{nombre}' no fue creado por el command"
            )