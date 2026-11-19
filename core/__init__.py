# core/__init__.py
"""Inicialización del paquete core del proyecto ERP Django.

Importa la app Celery para que se registre al arrancar Django.
Sin esta importación, @shared_task no encontraría la app Celery.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)