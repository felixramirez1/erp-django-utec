# proveedores/views.py
"""Vistas de la app proveedores — W02 (placeholder)."""
from django.shortcuts import render


def index(request):
    """Vista de índice de proveedores."""
    context = {
        'titulo': 'Proveedores',
        'descripcion': 'Red de proveedores de mercancía.',
        'espiral': 'Espiral 2 · W04',
    }
    return render(request, 'proveedores/index.html', context)
