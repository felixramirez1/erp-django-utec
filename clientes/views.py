# clientes/views.py
"""Vistas de la app clientes — W08.

Inicio: index (W02).
Lectura: ListView y DetailView.
Escritura: Create/Update/Delete.
"""
# Agregar PermissionRequiredMixin al import:
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ClienteForm
from .models import Cliente


def index(request):
    """Página de inicio de la app clientes (W02)."""
    return render(request, 'clientes/index.html')


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


class ClienteCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo cliente."""

    model         = Cliente
    form_class    = ClienteForm
    template_name = 'clientes/crear.html'
    success_url   = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Cliente "{self.object.nombre}" creado exitosamente.'
        )
        return response


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    """Formulario para editar un cliente."""

    model         = Cliente
    form_class    = ClienteForm
    template_name = 'clientes/editar.html'
    pk_url_kwarg  = 'cliente_id'
    success_url   = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Cliente "{self.object.nombre}" actualizado.'
        )
        return response


# Actualizar ClienteDeleteView:
class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model               = Cliente
    template_name       = 'clientes/eliminar.html'
    pk_url_kwarg        = 'cliente_id'
    success_url         = reverse_lazy('clientes:lista')
    permission_required = 'clientes.delete_cliente'
    raise_exception     = True

    def form_valid(self, form):
        nombre   = self.object.nombre
        response = super().form_valid(form)
        messages.success(self.request, f'Cliente "{nombre}" eliminado.')
        return response