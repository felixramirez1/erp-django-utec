# ventas/views.py
"""Vistas de la app ventas — W07.

Lectura: VentaListView y VentaDetailView.
Escritura (crear_venta): W08.
"""
# ventas/views.py — actualizar imports al inicio:
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# ventas/views.py — agregar imports al inicio:
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from .forms  import DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta

from django.views.generic import DetailView, ListView

from .models import Venta


class VentaListView(ListView):
    """Lista paginada de ventas en orden cronológico inverso."""

    model               = Venta
    template_name       = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by         = 20

    def get_queryset(self):
        """Pre-carga cliente para evitar N+1 en la tabla de ventas."""
        return (
            Venta.objects
            .select_related('cliente')
            .order_by('-fecha')
        )


class VentaDetailView(DetailView):
    """Detalle de una venta con todas sus líneas de producto."""

    model               = Venta
    template_name       = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg        = 'venta_id'

    def get_queryset(self):
        """Pre-carga cliente y prefetch líneas de detalle."""
        return (
            Venta.objects
            .select_related('cliente')
            .prefetch_related('detalles__producto')
        )
    
# Eliminar la función crear_venta de W08 y reemplazar por:

@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    """Crea un encabezado de venta con una línea de detalle.

    Decoradores (se aplican de abajo hacia arriba):
        @login_required            → verifica autenticación
        @permission_required(...)  → verifica permiso add_venta

    GET  → muestra los dos formularios vacíos.
    POST → valida ambos, guarda si correctos, muestra errores si no.
    """
    venta_form   = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta         = venta_form.save()
            detalle       = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            messages.success(
                request,
                f'Venta #{venta.pk} registrada. '
                f'Total: ${venta.total:.2f}'
            )
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form':   venta_form,
        'detalle_form': detalle_form,
    })

class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model               = Venta
    template_name       = 'ventas/eliminar.html'
    pk_url_kwarg        = 'venta_id'
    success_url         = reverse_lazy('ventas:lista')
    permission_required = 'ventas.delete_venta'
    raise_exception     = True

    def form_valid(self, form):
        pk       = self.object.pk
        response = super().form_valid(form)
        messages.success(self.request, f'Venta #{pk} eliminada.')
        return response