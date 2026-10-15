# proveedores/admin.py
"""Configuración del panel admin para la app proveedores."""
from django.contrib import admin

from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Admin de proveedores: lista, búsqueda y filtros."""

    list_display   = ['pk', 'nombre', 'contacto', 'correo',
                      'telefono', 'activo', 'creado']
    search_fields  = ['nombre', 'contacto', 'correo']
    list_filter    = ['activo']
    list_editable  = ['activo']
    readonly_fields = ['creado']
    date_hierarchy = 'creado'