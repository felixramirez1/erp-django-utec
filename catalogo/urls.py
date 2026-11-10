<<<<<<< HEAD
# catalogo/urls.py — agregar la URL del webhook:
from django.urls import path

from . import views
from .webhook_views import stripe_webhook
=======
# catalogo/urls.py — versión W14 (reemplaza el placeholder de W13)
"""URLs del módulo catálogo — W14."""
from django.urls import path

from . import views
>>>>>>> dba8f367ce4c962a023a6b2e2acc128e65909f18

app_name = 'catalogo'

urlpatterns = [
    # Catálogo público
<<<<<<< HEAD
    path('', views.CatalogoView.as_view(), name='catalogo'),

    # Carrito (W13)
    path('carrito/',                              views.ver_carrito,        name='carrito'),
    path('carrito/agregar/<int:producto_id>/',    views.agregar_al_carrito, name='agregar'),
    path('carrito/remover/<int:producto_id>/',    views.remover_del_carrito,name='remover'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar'),
    path('carrito/vaciar/',                       views.vaciar_carrito,     name='vaciar'),

    # Checkout con Stripe (W14)
    path('checkout/',                   views.checkout,    name='checkout'),
    path('pago-exitoso/<int:pedido_id>/', views.pago_exitoso, name='pago_exitoso'),
    path('pago-error/',                 views.pago_error,  name='pago_error'),

    # Webhook de Stripe (W15)
    path('webhook/', stripe_webhook, name='webhook'),
=======
    path('',
         views.CatalogoView.as_view(),
         name='catalogo'),

    # Carrito (W13)
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

    # Checkout con Stripe (W14)
    path('checkout/',
         views.checkout,
         name='checkout'),
    path('pago-exitoso/<int:pedido_id>/',
         views.pago_exitoso,
         name='pago_exitoso'),
    path('pago-error/',
         views.pago_error,
         name='pago_error'),
>>>>>>> dba8f367ce4c962a023a6b2e2acc128e65909f18
]