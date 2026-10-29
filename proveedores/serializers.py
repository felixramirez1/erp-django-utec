# proveedores/serializers.py
"""Serializers de la app proveedores — W10."""
from rest_framework import serializers

from .models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer de Proveedor — todos los campos."""

    class Meta:
        model  = Proveedor
        fields = ['id', 'nombre', 'contacto', 'correo',
                  'telefono', 'activo', 'creado']
        read_only_fields = ['id', 'creado']