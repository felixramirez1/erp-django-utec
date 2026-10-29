# ventas/api_views.py
"""Vistas de la API REST para ventas — W10."""
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from .models      import Venta
from .serializers import VentaSerializer


class VentaListCreateAPIView(ListCreateAPIView):
    """GET /api/ventas/ · POST /api/ventas/"""

    serializer_class = VentaSerializer

    def get_queryset(self):
        return (
            Venta.objects
            .select_related('cliente')
            .prefetch_related('detalles__producto')
            .order_by('-fecha')
        )


class VentaDetailAPIView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/ventas/<id>/"""

    serializer_class = VentaSerializer

    def get_queryset(self):
        return (
            Venta.objects
            .select_related('cliente')
            .prefetch_related('detalles__producto')
        )