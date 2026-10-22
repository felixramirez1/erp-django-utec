# core/management/commands/crear_grupos.py
"""Management command para crear los 3 grupos de acceso del ERP.

Uso:
    python manage.py crear_grupos

Crea o actualiza los grupos:
    Gerente  → acceso completo a todas las apps del ERP
    Vendedor → operar ventas, consultar productos y clientes
    Almacén  → gestionar inventario de productos

Ejecutar en producción después de cada deploy para sincronizar permisos.
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from clientes.models       import Cliente
from configuracion.models  import ConfiguracionERP
from productos.models      import Categoria, Producto
from proveedores.models    import Proveedor
from ventas.models         import DetalleVenta, Pedido, Venta


def _permisos(*modelos: type, acciones=('add', 'change', 'delete', 'view')):
    """Obtiene permisos de las acciones indicadas para los modelos dados.

    Args:
        *modelos: clases de modelo Django.
        acciones: tupla de acciones (add, change, delete, view).

    Returns:
        QuerySet de Permission filtrado.
    """
    ct_ids = [
        ContentType.objects.get_for_model(m).pk
        for m in modelos
    ]
    return Permission.objects.filter(
        content_type_id__in=ct_ids,
        codename__in=[
            f'{accion}_{m._meta.model_name}'
            for m in modelos
            for accion in acciones
        ]
    )


class Command(BaseCommand):
    help = 'Crea o actualiza los 3 grupos de acceso del ERP'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(
            '\nConfigurando grupos de acceso del ERP...\n'
        ))

        # ── GERENTE: acceso completo ────────────────────────────────────
        gerente, creado = Group.objects.get_or_create(name='Gerente')
        permisos_gerente = _permisos(
            Cliente, Proveedor, Categoria, Producto,
            Venta, DetalleVenta, Pedido, ConfiguracionERP,
            acciones=('add', 'change', 'delete', 'view')
        )
        gerente.permissions.set(permisos_gerente)
        self.stdout.write(self.style.SUCCESS(
            f'  ✅ Gerente — {permisos_gerente.count()} permisos asignados'
            f' ({"creado" if creado else "actualizado"})'
        ))

        # ── VENDEDOR: operar ventas, consultar productos y clientes ─────
        vendedor, creado = Group.objects.get_or_create(name='Vendedor')
        permisos_vendedor = _permisos(
            Venta, DetalleVenta,
            acciones=('add', 'view')
        ) | _permisos(
            Producto, Cliente,
            acciones=('view',)
        )
        vendedor.permissions.set(permisos_vendedor)
        self.stdout.write(self.style.SUCCESS(
            f'  ✅ Vendedor — {permisos_vendedor.count()} permisos asignados'
            f' ({"creado" if creado else "actualizado"})'
        ))

        # ── ALMACÉN: gestionar inventario ───────────────────────────────
        almacen, creado = Group.objects.get_or_create(name='Almacén')
        permisos_almacen = _permisos(
            Producto, Categoria,
            acciones=('add', 'change', 'view')
        ) | _permisos(
            Proveedor,
            acciones=('view',)
        )
        almacen.permissions.set(permisos_almacen)
        self.stdout.write(self.style.SUCCESS(
            f'  ✅ Almacén — {permisos_almacen.count()} permisos asignados'
            f' ({"creado" if creado else "actualizado"})'
        ))

        self.stdout.write(self.style.SUCCESS(
            '\n🎉 Grupos configurados exitosamente.\n'
            'Asigna usuarios desde /admin/ → Usuarios → Grupos.\n'
        ))