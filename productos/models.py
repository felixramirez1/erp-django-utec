# productos/models.py
"""Modelos de la app productos — Espiral 2 W05.

Orden de implementación:
  1. Categoria  (sin FK)
  2. Producto   (FK → Categoria, FK → Proveedor)  ← Parte 3
"""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from proveedores.models import Proveedor


class Categoria(models.Model):
    """Categoría para clasificar productos del catálogo.

    Atributos:
        nombre:      Nombre único de la categoría.
        descripcion: Descripción opcional.
    """

    nombre      = models.CharField(
        max_length=100, unique=True, verbose_name='Nombre'
    )
    descripcion = models.TextField(
        blank=True, verbose_name='Descripción'
    )

    class Meta:
        verbose_name        = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering            = ['nombre']

    def __str__(self) -> str:
        return self.nombre
    
# Agregar después de la clase Categoria en productos/models.py

class Producto(models.Model):
    """Artículo del inventario del ERP.

    Decisiones de diseño aplicadas:
        D-01: categoria usa on_delete=PROTECT.
        D-02: proveedor usa on_delete=SET_NULL (puede ser null).
    """

    nombre    = models.CharField(
        max_length=200, verbose_name='Nombre'
    )
    precio    = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio ($)',
        help_text='El precio no puede ser negativo.'
    )
    stock     = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock disponible'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,          # D-01: no borrar categoría con productos
        related_name='productos',
        verbose_name='Categoría'
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,         # D-02: producto puede quedar sin proveedor
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Proveedor'
    )
    activo    = models.BooleanField(
        default=True, verbose_name='Activo'
    )
    creado    = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de registro'
    )

    class Meta:
        verbose_name        = 'Producto'
        verbose_name_plural = 'Productos'
        ordering            = ['nombre']

    def __str__(self) -> str:
        return f"{self.nombre} (${self.precio:.2f})"