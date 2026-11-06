# catalogo/context_processors.py
"""Context processors de la app catalogo — W13.

carrito_info: inyecta el contador de items del carrito en todos
              los templates, permitiendo mostrarlo en la navbar
              de base.html sin necesidad de pasarlo manualmente
              en cada vista.
"""
from typing import Any


def carrito_info(request) -> dict[str, Any]:
    """Calcula el total de items en el carrito y lo inyecta globalmente.

    Returns:
        dict con:
            carrito_total_items (int): número total de unidades en el carrito.
            carrito_total_productos (int): número de productos distintos.
    """
    carrito = request.session.get('carrito', {})

    total_items     = sum(
        int(item.get('cantidad', 0)) for item in carrito.values()
    )
    total_productos = len(carrito)

    return {
        'carrito_total_items':     total_items,
        'carrito_total_productos': total_productos,
    }