# clientes/serializers.py
"""Serializers de la app clientes — W10."""
from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer de Cliente — todos los campos públicos."""

    class Meta:
        model  = Cliente
        fields = ['id', 'nombre', 'correo', 'telefono', 'activo', 'creado']
        read_only_fields = ['id', 'creado']