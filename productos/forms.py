# productos/forms.py
"""Formularios de la app productos — W08."""
from django import forms

from .models import Producto


# productos/forms.py — actualizar la clase ProductoForm:
class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos — W11.

    Incluye campo imagen con widget de archivo.
    El template debe usar enctype="multipart/form-data".
    """

    class Meta:
        model  = Producto
        fields = ['nombre', 'precio', 'stock', 'categoria',
                  'proveedor', 'activo', 'imagen']   # ← agregar imagen
        widgets = {
            'nombre':    forms.TextInput(
                attrs={'class': 'erp-input',
                       'placeholder': 'Nombre del producto'}
            ),
            'precio':    forms.NumberInput(
                attrs={'class': 'erp-input', 'step': '0.01', 'min': '0'}
            ),
            'stock':     forms.NumberInput(
                attrs={'class': 'erp-input', 'min': '0'}
            ),
            'categoria': forms.Select(attrs={'class': 'erp-input'}),
            'proveedor': forms.Select(attrs={'class': 'erp-input'}),
            'imagen':    forms.ClearableFileInput(
                attrs={'class': 'erp-input',
                       'accept': 'image/jpeg,image/png,image/webp'}
            ),
        }
        labels = {
            'nombre':    'Nombre',
            'precio':    'Precio ($)',
            'stock':     'Stock disponible',
            'categoria': 'Categoría',
            'proveedor': 'Proveedor',
            'activo':    'Activo',
            'imagen':    'Imagen del producto',
        }