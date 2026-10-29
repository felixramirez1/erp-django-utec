# proveedores/api_views.py
"""Vistas de la API REST para proveedores — W10."""
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from .models      import Proveedor
from .serializers import ProveedorSerializer


class ProveedorListCreateAPIView(ListCreateAPIView):
    """GET /api/proveedores/ · POST /api/proveedores/"""

    queryset         = Proveedor.objects.filter(activo=True).order_by('nombre')
    serializer_class = ProveedorSerializer


class ProveedorDetailAPIView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/proveedores/<id>/"""

    queryset         = Proveedor.objects.all()
    serializer_class = ProveedorSerializer