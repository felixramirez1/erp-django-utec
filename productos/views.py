# productos/views.py
"""Vistas de la app productos — W07.

ListView y DetailView con select_related y paginación.
Escritura (Create/Update/Delete) se implementa en W08.
"""
# productos/views.py — actualizar el import al inicio:
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ProductoForm
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

class ProductoCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo producto.

    LoginRequiredMixin PRIMERO en la herencia (obligatorio).
    Redirige a /accounts/login/ si el usuario no está autenticado.
    """

    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/crear.html'
    success_url   = reverse_lazy('productos:lista')  # reverse_lazy (no reverse)

    def form_valid(self, form):
        """Agrega mensaje flash de éxito al guardar."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" creado exitosamente.'
        )
        return response


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    """Formulario para editar un producto existente."""

    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/editar.html'
    pk_url_kwarg  = 'producto_id'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" actualizado.'
        )
        return response

class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model               = Producto
    template_name       = 'productos/eliminar.html'
    pk_url_kwarg        = 'producto_id'
    success_url         = reverse_lazy('productos:lista')
    permission_required = 'productos.delete_producto'
    # (sin raise_exception)