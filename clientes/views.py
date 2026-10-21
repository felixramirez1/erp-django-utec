# clientes/views.py
"""Vistas de la app clientes — W07.

Lectura: ListView y DetailView.
Escritura (Create/Update/Delete): W08.
"""
from django.views.generic import DetailView, ListView

from .models import Cliente


class ClienteListView(ListView):
    """Lista paginada de clientes activos."""

    model               = Cliente
    template_name       = 'clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by         = 20

    def get_queryset(self):
        return Cliente.objects.filter(activo=True).order_by('nombre')


class ClienteDetailView(DetailView):
    """Detalle de un cliente con su historial de ventas."""

    model               = Cliente
    template_name       = 'clientes/detalle.html'
    context_object_name = 'cliente'
    pk_url_kwarg        = 'cliente_id'

    def get_context_data(self, **kwargs):
        """Agrega las ventas del cliente al contexto."""
        ctx = super().get_context_data(**kwargs)
        ctx['ventas'] = (
            self.object.ventas
            .order_by('-fecha')[:10]   # últimas 10 ventas
        )
        return ctx