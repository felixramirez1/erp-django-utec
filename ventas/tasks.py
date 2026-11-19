# ventas/tasks.py
"""Tareas asíncronas de la app ventas — W16.

Las tareas con @shared_task son descubiertas automáticamente
por celery.autodiscover_tasks() definido en core/celery.py.

Estado de implementación:
    W16: Estructura base — las tareas solo registran en el log.
    W17: Se agrega SendGrid para envío real de correos.
    W18: Se agregan tareas programadas con Celery Beat.

Uso:
    # Desde una vista (asíncrono — no bloquea la respuesta HTTP):
    enviar_confirmacion_pedido.delay(pedido_id)

    # Desde la línea de comandos (síncrono — para depuración):
    python manage.py shell
    >>> from ventas.tasks import enviar_confirmacion_pedido
    >>> result = enviar_confirmacion_pedido.apply(args=[1])
    >>> result.get()
"""
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,      # esperar 60s antes de reintentar
    name='ventas.enviar_confirmacion_pedido',
)
def enviar_confirmacion_pedido(self, pedido_id: int) -> dict:
    """Envía el correo de confirmación de pedido al cliente.

    W16: Solo registra en el log (placeholder).
    W17: Enviará correo real con SendGrid.

    Args:
        pedido_id: ID del Pedido confirmado.

    Returns:
        dict con estado y pedido_id procesado.
    """
    from ventas.models import Pedido   # import local evita circularidad

    try:
        pedido = Pedido.objects.select_related('cliente').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(
            f'[Tarea enviar_confirmacion] Pedido {pedido_id} no existe.'
        )
        return {'estado': 'error', 'pedido_id': pedido_id}

    # W16: Placeholder — solo registra en el log
    logger.info(
        f'[Tarea enviar_confirmacion] Procesando pedido '
        f'{pedido.numero_pedido} para {pedido.cliente.correo}. '
        f'Total: ${pedido.total_pagado}. '
        f'Timestamp: {timezone.now().isoformat()}'
    )

    # W17 implementará aquí:
    #   from django.core.mail import send_mail
    #   o envío via SendGrid API

    return {
        'estado':    'ok',
        'pedido_id': pedido_id,
        'numero':    pedido.numero_pedido,
        'cliente':   pedido.cliente.correo,
    }


@shared_task(
    bind=True,
    max_retries=1,
    name='ventas.verificar_stock_bajo',
)
def verificar_stock_bajo(self, umbral: int = 5) -> dict:
    """Verifica productos con stock por debajo del umbral.

    W16: Solo registra en el log (placeholder).
    W17: Enviará alerta por correo al administrador.
    W18: Se programa para ejecutarse automáticamente cada hora.

    Args:
        umbral: cantidad mínima de stock antes de alertar (default: 5).

    Returns:
        dict con lista de productos con stock bajo.
    """
    from productos.models import Producto   # import local

    productos_bajos = list(
        Producto.objects
        .filter(activo=True, stock__lt=umbral)
        .values('pk', 'nombre', 'stock')
        .order_by('stock')
    )

    if productos_bajos:
        logger.warning(
            f'[Tarea verificar_stock] {len(productos_bajos)} producto(s) '
            f'con stock < {umbral}: '
            f'{[p["nombre"] for p in productos_bajos]}'
        )
    else:
        logger.info(
            f'[Tarea verificar_stock] Todos los productos tienen '
            f'stock >= {umbral}. OK.'
        )

    return {
        'umbral':          umbral,
        'productos_bajos': productos_bajos,
        'total':           len(productos_bajos),
    }