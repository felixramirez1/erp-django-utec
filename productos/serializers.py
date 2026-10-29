# productos/serializers.py — versión W11
"""Serializers de la app productos — W11.

Novedades respecto a W10:
    ProductoSerializer: agrega imagen_url (URL absoluta de la imagen).
"""
from rest_framework import serializers

from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer de Categoria — sin cambios respecto a W10."""

    class Meta:
        model            = Categoria
        fields           = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de Producto con URL absoluta de imagen.

    imagen_url: URL completa de la imagen del producto.
                None si el producto no tiene imagen.
                Requiere que el contexto incluya 'request'
                (automático en vistas APIView).
    """

    categoria_nombre = serializers.CharField(
        source='categoria.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True,
        allow_null=True
    )
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = [
            'id', 'nombre', 'precio', 'stock',
            'categoria', 'categoria_nombre',
            'proveedor', 'proveedor_nombre',
            'activo', 'imagen', 'imagen_url', 'creado',
        ]
        read_only_fields = [
            'id', 'creado',
            'categoria_nombre', 'proveedor_nombre',
            'imagen_url',       # solo lectura — se construye en get_imagen_url
        ]
        extra_kwargs = {
            'imagen': {'required': False, 'allow_null': True},
        }

    def get_imagen_url(self, obj: Producto) -> str | None:
        """Devuelve la URL absoluta de la imagen del producto.

        Args:
            obj: instancia de Producto.

        Returns:
            URL absoluta como string, o None si no hay imagen.
        """
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        if obj.imagen:
            return obj.imagen.url   # fallback sin request (tests)
        return None