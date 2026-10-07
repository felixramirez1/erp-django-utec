# ventas/views.py
"""Vistas de la app ventas — W02 (placeholder)."""
from django.shortcuts import render


def index(request):
    """Vista de índice de ventas."""
    context = {
        'titulo': 'Ventas',
        'descripcion': 'Ciclo de ventas, pedidos y facturación.',
        'espiral': 'Espiral 3 · W07',
    }
    return render(request, 'ventas/index.html', context)
