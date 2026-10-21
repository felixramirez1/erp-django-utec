# productos/views.py
"""Vistas de la app productos — W07.

ListView y DetailView con select_related y paginación.
Escritura (Create/Update/Delete) se implementa en W08.
"""
from django.views.generic import DetailView, ListView

from .models import Producto


class ProductoListView(ListView):
    """Lista paginada de productos activos.

    Atributos:
        model:               Modelo a listar.
        template_name:       Plantilla HTML (Fable 5 AzulERP).
        context_object_name: Nombre de la variable en el template.
        paginate_by:         20 productos por página.
        queryset:            Solo productos activos, con FK pre-cargadas.
    """

    model               = Producto
    template_name       = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by         = 20

    def get_queryset(self):
        """Devuelve productos activos con FKs pre-cargadas (evita N+1)."""
        return (
            Producto.objects
            .select_related('categoria', 'proveedor')
            .filter(activo=True)
            .order_by('nombre')
        )


class ProductoDetailView(DetailView):
    """Detalle de un producto por ID de URL.

    Atributos:
        model:               Modelo a mostrar.
        template_name:       Plantilla HTML.
        context_object_name: Nombre en el template ('producto').
        pk_url_kwarg:        Parámetro de URL. Usa 'producto_id'
                             para ser consistente con W02.
    """

    model               = Producto
    template_name       = 'productos/detalle.html'
    context_object_name = 'producto'
    pk_url_kwarg        = 'producto_id'

    def get_queryset(self):
        """Pre-carga FKs para evitar queries adicionales en el template."""
        return Producto.objects.select_related('categoria', 'proveedor')