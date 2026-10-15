# productos/admin.py
"""Configuración del panel admin para la app productos."""
from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Admin de categorías."""

    list_display  = ['pk', 'nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin de productos: lista con categoría, proveedor y stock."""

    list_display   = ['pk', 'nombre', 'precio', 'stock',
                      'categoria', 'proveedor', 'activo', 'creado']
    search_fields  = ['nombre', 'categoria__nombre', 'proveedor__nombre']
    list_filter    = ['activo', 'categoria']
    list_editable  = ['precio', 'stock', 'activo']
    readonly_fields = ['creado']
    autocomplete_fields = ['proveedor']     # requiere search_fields en Proveedor
    date_hierarchy = 'creado'
    ordering       = ['nombre']