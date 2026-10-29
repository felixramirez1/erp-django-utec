# productos/api_views.py
"""Vistas de la API REST para la app productos — W10.

Usa vistas genéricas de DRF:
    ListCreateAPIView            → GET lista + POST crear
    RetrieveUpdateDestroyAPIView → GET/PUT/PATCH/DELETE por ID
"""
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from .models       import Categoria, Producto
from .serializers  import CategoriaSerializer, ProductoSerializer


# ── Categoria ──────────────────────────────────────────────────────────────

class CategoriaListCreateAPIView(ListCreateAPIView):
    """GET /api/categorias/ · POST /api/categorias/"""

    queryset         = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer


class CategoriaDetailAPIView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/categorias/<id>/"""

    queryset         = Categoria.objects.all()
    serializer_class = CategoriaSerializer


# ── Producto ───────────────────────────────────────────────────────────────

class ProductoListCreateAPIView(ListCreateAPIView):
    """GET /api/productos/ · POST /api/productos/

    GET sin autenticación → 200 (IsAuthenticatedOrReadOnly).
    POST sin token → 403.
    POST con token → 201.
    """

    serializer_class = ProductoSerializer

    def get_queryset(self):
        """Solo productos activos con FKs pre-cargadas."""
        return (
            Producto.objects
            .select_related('categoria', 'proveedor')
            .filter(activo=True)
            .order_by('nombre')
        )


class ProductoDetailAPIView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/productos/<id>/"""

    serializer_class = ProductoSerializer

    def get_queryset(self):
        return Producto.objects.select_related('categoria', 'proveedor')