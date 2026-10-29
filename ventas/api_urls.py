# ventas/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('ventas/',          api_views.VentaListCreateAPIView.as_view()),
    path('ventas/<int:pk>/', api_views.VentaDetailAPIView.as_view()),
]