# clientes/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('clientes/',          api_views.ClienteListCreateAPIView.as_view()),
    path('clientes/<int:pk>/', api_views.ClienteDetailAPIView.as_view()),
]