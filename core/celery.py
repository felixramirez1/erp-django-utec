# core/celery.py
"""Configuración de la aplicación Celery para el proyecto ERP Django.

Este archivo debe importarse ANTES de cualquier tarea (@shared_task)
para que Celery esté configurado correctamente.

Uso desde la línea de comandos:
    # Iniciar worker (procesa tareas)
    celery -A core worker -l info

    # Iniciar worker + Beat (procesa tareas + tareas programadas)
    celery -A core worker -B -l info

    # Monitorear con Flower
    celery -A core flower --port=5555
"""
import os

from celery import Celery

# Establecer el módulo de settings de Django antes de crear la app Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Crear la aplicación Celery con el nombre del proyecto
app = Celery('core')

# Leer la configuración desde Django settings
# El prefijo CELERY_ distingue las variables de Celery de otras de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todos los archivos tasks.py de las apps instaladas
# Django buscará: clientes/tasks.py, productos/tasks.py, ventas/tasks.py, etc.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tarea de diagnóstico — muestra el request de la tarea.

    Ejecutar para verificar que el worker está funcionando:
        from core.celery import debug_task
        debug_task.delay()
    """
    print(f'Request: {self.request!r}')