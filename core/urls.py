# core/urls.py
"""Enrutador principal del ERP Django — W09."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/',       admin.site.urls),
    path('',             views.bienvenida,             name='inicio'),
    # Allauth (login / logout / registro)
    path('accounts/',    include('allauth.urls')),     # ← agregar
    # Apps del ERP
    path('clientes/',    include('clientes.urls',    namespace='clientes')),
    path('proveedores/', include('proveedores.urls', namespace='proveedores')),
    path('productos/',   include('productos.urls',   namespace='productos')),
    path('ventas/',      include('ventas.urls',       namespace='ventas')),
    path('reportes/',    include('reportes.urls',     namespace='reportes')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)