# proveedores/forms.py
"""Formularios de la app proveedores — W08."""
from django import forms

from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    """Formulario para crear y editar proveedores."""

    class Meta:
        model  = Proveedor
        fields = ['nombre', 'contacto', 'correo', 'telefono', 'activo']
        widgets = {
            'nombre':   forms.TextInput(
                attrs={'class': 'erp-input',
                       'placeholder': 'Nombre comercial'}
            ),
            'contacto': forms.TextInput(
                attrs={'class': 'erp-input',
                       'placeholder': 'Nombre de la persona de contacto'}
            ),
            'correo':   forms.EmailInput(
                attrs={'class': 'erp-input'}
            ),
            'telefono': forms.TextInput(
                attrs={'class': 'erp-input'}
            ),
        }