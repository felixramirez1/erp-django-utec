# clientes/models.py
"""Modelos de la app clientes — Espiral 2 W05."""
from django.db import models


class Cliente(models.Model):
    """Representa a un cliente del sistema ERP.

    Atributos:
        nombre:   Nombre completo o razón social.
        correo:   Correo electrónico único (identificador principal).
        telefono: Teléfono de contacto (opcional).
        activo:   Soft-delete: False = dado de baja sin borrar historial.
        creado:   Fecha de registro (automática, inmutable).
    """

    nombre   = models.CharField(
        max_length=150, verbose_name='Nombre'
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
        verbose_name        = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering            = ['nombre']

    def __str__(self) -> str:
        return self.nombre