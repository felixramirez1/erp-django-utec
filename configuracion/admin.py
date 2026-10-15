# configuracion/admin.py
"""Configuración del panel admin para ConfiguracionERP (singleton)."""
from django.contrib import admin

from .models import ConfiguracionERP


@admin.register(ConfiguracionERP)
class ConfiguracionERPAdmin(admin.ModelAdmin):
    """Admin de configuración global.

    Al ser singleton (D-07), se deshabilita el botón 'Agregar'
    para evitar crear más de un registro.
    """

    list_display = ['nombre_empresa', 'rfc', 'moneda', 'iva_porcentaje']

    def has_add_permission(self, request) -> bool:
        """Deshabilita el botón 'Agregar' si ya existe el registro."""
        return not ConfiguracionERP.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        """No permitir borrar la configuración del sistema."""
        return False