# clientes/admin.py
"""Configuración del panel admin para la app clientes."""
from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Admin de clientes: lista, búsqueda y filtros."""

    list_display   = ['pk', 'nombre', 'correo', 'telefono',
                      'activo', 'creado']
    search_fields  = ['nombre', 'correo', 'telefono']
    list_filter    = ['activo']
    list_editable  = ['activo']
    readonly_fields = ['creado']
    date_hierarchy = 'creado'
    ordering       = ['nombre']