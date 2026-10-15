# configuracion/models.py
"""Modelo de configuración global del sistema ERP — Espiral 2 W05.

Decisión D-07: singleton — siempre existe exactamente un registro (pk=1).
"""
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ConfiguracionERP(models.Model):
    """Configuración global del sistema ERP.

    Implementa el patrón Singleton: save() fuerza pk=1, garantizando
    que solo exista un registro en la base de datos.

    Uso:
        config = ConfiguracionERP.get_instance()
        print(config.nombre_empresa)
    """

    nombre_empresa = models.CharField(
        max_length=200, verbose_name='Nombre de la empresa'
    )
    rfc            = models.CharField(
        max_length=13, blank=True, verbose_name='RFC'
    )
    moneda         = models.CharField(
        max_length=3,
        default='MXN',
        verbose_name='Moneda (ISO 4217)',
        help_text='Ejemplos: MXN, USD, EUR'
    )
    iva_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00')),
        ],
        verbose_name='IVA (%)'
    )
    logo           = models.ImageField(
        upload_to='configuracion/',
        null=True, blank=True,
        verbose_name='Logo de la empresa'
    )

    class Meta:
        verbose_name        = 'Configuración ERP'
        verbose_name_plural = 'Configuración ERP'

    def __str__(self) -> str:
        return f"{self.nombre_empresa} — IVA {self.iva_porcentaje}%"

    def save(self, *args, **kwargs) -> None:
        """Fuerza pk=1 para garantizar el patrón singleton (D-07)."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls) -> 'ConfiguracionERP':
        """Obtiene o crea la instancia única de configuración.

        Returns:
            ConfiguracionERP: la única instancia del sistema.
        """
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'nombre_empresa': 'Mi Empresa ERP',
                'moneda':         'MXN',
                'iva_porcentaje': Decimal('16.00'),
            }
        )
        return obj