# proveedores/models.py
"""Modelos de la app proveedores — Espiral 2 W05."""
from django.db import models


class Proveedor(models.Model):
    """Representa a un proveedor de mercancía.

    Atributos:
        nombre:   Nombre comercial o razón social.
        contacto: Persona de contacto (opcional).
        correo:   Correo electrónico único.
        telefono: Teléfono (opcional).
        activo:   Soft-delete.
        creado:   Fecha de registro (automática).
    """

    nombre   = models.CharField(
        max_length=150, verbose_name='Nombre'
    )
    contacto = models.CharField(
        max_length=100, blank=True, verbose_name='Persona de contacto'
    )
    correo   = models.EmailField(
        unique=True, verbose_name='Correo electrónico'
    )
    telefono = models.CharField(
        max_length=20, blank=True, verbose_name='Teléfono'
    )
    activo   = models.BooleanField(
        default=True, verbose_name='Activo'
    )
    creado   = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de registro'
    )

    class Meta:
        verbose_name        = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering            = ['nombre']

    def __str__(self) -> str:
        return self.nombre