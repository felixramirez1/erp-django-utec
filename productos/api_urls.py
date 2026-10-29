# productos/api_urls.py
"""URLs de la API REST para la app productos — W10."""
from django.urls import path
from . import api_views

urlpatterns = [
    path('categorias/',      api_views.CategoriaListCreateAPIView.as_view()),
    path('categorias/<int:pk>/', api_views.CategoriaDetailAPIView.as_view()),
    path('productos/',       api_views.ProductoListCreateAPIView.as_view()),
    path('productos/<int:pk>/',  api_views.ProductoDetailAPIView.as_view()),
]