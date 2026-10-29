# ventas/serializers.py
"""Serializers de la app ventas — W10.

Nota sobre Venta.total:
    Es una @property calculada en tiempo de ejecución.
    No existe como campo en la BD.
    Se expone en la API como SerializerMethodField (solo lectura).
"""
from decimal import Decimal

from rest_framework import serializers

from .models import DetalleVenta, Venta


class DetalleVentaSerializer(serializers.ModelSerializer):
    """Serializer de línea de detalle con subtotal calculado."""

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model  = DetalleVenta
        fields = ['id', 'producto', 'cantidad',
                  'precio_unitario', 'subtotal']
        read_only_fields = ['id', 'subtotal']

    def get_subtotal(self, obj: DetalleVenta) -> Decimal:
        """Calcula el subtotal: cantidad × precio_unitario."""
        return obj.subtotal


class VentaSerializer(serializers.ModelSerializer):
    """Serializer de Venta con detalles anidados y total calculado.

    detalles: lista de líneas de detalle (solo lectura en este serializer).
    total:    propiedad calculada, no campo de BD (D-04).
    """

    detalles      = DetalleVentaSerializer(many=True, read_only=True)
    total         = serializers.SerializerMethodField()
    cliente_nombre = serializers.CharField(
        source='cliente.nombre',
        read_only=True
    )

    class Meta:
        model  = Venta
        fields = ['id', 'cliente', 'cliente_nombre',
                  'fecha', 'detalles', 'total']
        read_only_fields = ['id', 'fecha', 'detalles',
                            'total', 'cliente_nombre']

    def get_total(self, obj: Venta) -> Decimal:
        """Devuelve el total calculado de la venta."""
        return obj.total