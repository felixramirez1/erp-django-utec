# catalogo/urls.py
"""URLs del módulo catálogo — W13."""
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'catalogo'

urlpatterns = [
    # Catálogo público
    path('',
         views.CatalogoView.as_view(),
         name='catalogo'),
    # Carrito
    path('carrito/',
         views.ver_carrito,
         name='carrito'),
    path('carrito/agregar/<int:producto_id>/',
         views.agregar_al_carrito,
         name='agregar'),
    path('carrito/remover/<int:producto_id>/',
         views.remover_del_carrito,
         name='remover'),
    path('carrito/actualizar/<int:producto_id>/',
         views.actualizar_cantidad,
         name='actualizar'),
    path('carrito/vaciar/',
         views.vaciar_carrito,
         name='vaciar'),
    # Checkout — se implementa en W14
    path('checkout/',
         TemplateView.as_view(
             template_name='catalogo/checkout_pendiente.html'
         ),
         name='checkout'),
]

