# proveedores/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('proveedores/',          api_views.ProveedorListCreateAPIView.as_view()),
    path('proveedores/<int:pk>/', api_views.ProveedorDetailAPIView.as_view()),
]