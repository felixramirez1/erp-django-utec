# ventas/tasks.py
"""Tareas asíncronas de la app ventas — W17.

W16: estructura base (solo log).
W17: envío real de correos con django-anymail + SendGrid.
W18: tareas programadas con Celery Beat.

Idempotencia:
    Pedido.correo_enviado=True previene envíos duplicados si la tarea
    se llama más de una vez para el mismo pedido (p. ej. Stripe reenvía
    el webhook o Celery reintenta).

Uso:
    # Desde una vista o el webhook (asíncrono):
    enviar_confirmacion_pedido.delay(pedido_id)

    # Depuración en el shell (síncrono):
    >>> from ventas.tasks import enviar_confirmacion_pedido
    >>> enviar_confirmacion_pedido.apply(args=[1]).get()
"""
import logging
from decimal import Decimal, InvalidOperation

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)


def _url_absoluta(nombre_url: str) -> str:
    """Construye una URL absoluta sin request (las tareas no tienen request).

    Usa settings.SITE_URL (en Render: RENDER_EXTERNAL_URL automática).
    """
    return f'{settings.SITE_URL}{reverse(nombre_url)}'


def _items_con_subtotal(items_snapshot: list) -> list:
    """Agrega 'subtotal' (precio × cantidad, Decimal) a cada item del snapshot.

    Se calcula en Python porque {% widthratio %} redondea a entero
    y perdería los centavos.
    """
    items = []
    for item in items_snapshot or []:
        try:
            precio   = Decimal(str(item.get('precio', '0')))
            cantidad = int(item.get('cantidad', 0))
        except (InvalidOperation, TypeError, ValueError):
            precio, cantidad = Decimal('0.00'), 0
        items.append({
            **item,
            'precio':   precio.quantize(Decimal('0.01')),
            'cantidad': cantidad,
            'subtotal': (precio * cantidad).quantize(Decimal('0.01')),
        })
    return items


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='ventas.enviar_confirmacion_pedido',
)
def enviar_confirmacion_pedido(self, pedido_id: int) -> dict:
    """Envía el correo de confirmación de pedido al cliente.

    Garantías:
        - Idempotente: si correo_enviado=True, aborta sin error.
        - Retry automático hasta 3 veces si SendGrid falla.

    Args:
        pedido_id: ID del Pedido confirmado.

    Returns:
        dict con estado, pedido_id y correo del destinatario.
    """
    from configuracion.models import ConfiguracionERP  # import local
    from ventas.models        import Pedido             # import local

    try:
        pedido = Pedido.objects.select_related('cliente').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'[correo_confirmacion] Pedido {pedido_id} no existe.')
        return {
            'estado':    'error',
            'pedido_id': pedido_id,
            'razon':     'Pedido no encontrado',
        }

    # ── Verificación de idempotencia ────────────────────────────────────
    if pedido.correo_enviado:
        logger.info(
            f'[correo_confirmacion] Pedido {pedido.numero_pedido}: '
            f'correo ya enviado anteriormente — skip.'
        )
        return {
            'estado':    'skip',
            'pedido_id': pedido_id,
            'razon':     'correo ya enviado',
        }

    config = ConfiguracionERP.get_instance()

    # ── Contexto del correo ─────────────────────────────────────────────
    contexto = {
        'pedido':     pedido,
        'config':     config,
        'items':      _items_con_subtotal(pedido.items_snapshot),
        'url_tienda': _url_absoluta('catalogo:catalogo'),
    }

    # ── Renderizar templates (sin request) ──────────────────────────────
    asunto = (
        f'Confirmación de pedido {pedido.numero_pedido} '
        f'— {config.nombre_empresa}'
    )
    texto_plano = render_to_string('emails/confirmacion_pedido.txt',  contexto)
    html_body   = render_to_string('emails/confirmacion_pedido.html', contexto)

    correo_destino = pedido.cliente.correo

    mensaje = EmailMultiAlternatives(
        subject    = asunto,
        body       = texto_plano,          # versión texto plano (fallback)
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [correo_destino],
    )
    mensaje.attach_alternative(html_body, 'text/html')

    # ── Enviar y manejar errores ────────────────────────────────────────
    try:
        mensaje.send()
    except Exception as exc:
        logger.error(
            f'[correo_confirmacion] Error al enviar correo para pedido '
            f'{pedido.numero_pedido}: {exc}'
        )
        # Reintento con espera creciente: 60 s, 120 s, 180 s
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

    # Marcar como enviado (update() no pisa otros campos del pedido)
    Pedido.objects.filter(pk=pedido.pk).update(correo_enviado=True)
    logger.info(
        f'[correo_confirmacion] Correo enviado a {correo_destino} '
        f'para pedido {pedido.numero_pedido}.'
    )
    return {
        'estado':    'ok',
        'pedido_id': pedido_id,
        'correo':    correo_destino,
    }


@shared_task(
    bind=True,
    max_retries=1,
    name='ventas.verificar_stock_bajo',
)
def verificar_stock_bajo(self, umbral: int = 5) -> dict:
    """Verifica productos con stock bajo y envía alerta al admin.

    W17: si hay productos bajo el umbral, envía correo a ADMINS[0].
    W18: se programa con Celery Beat.

    Args:
        umbral: cantidad mínima antes de alertar (default: 5).

    Returns:
        dict con umbral, total, productos_bajos y alerta_enviada.
    """
    from productos.models import Producto   # import local

    productos_bajos = list(
        Producto.objects
        .filter(activo=True, stock__lt=umbral)
        .values('pk', 'nombre', 'stock', 'categoria__nombre')
        .order_by('stock')
    )

    if not productos_bajos:
        logger.info(
            f'[stock_bajo] Todos los productos tienen stock >= {umbral}. OK.'
        )
        return {
            'umbral': umbral, 'total': 0,
            'productos_bajos': [], 'alerta_enviada': False,
        }

    logger.warning(
        f'[stock_bajo] {len(productos_bajos)} producto(s) con stock < {umbral}.'
    )

    alerta_enviada = False
    if settings.ADMINS:
        alerta_enviada = _enviar_alerta_stock(productos_bajos, umbral)

    return {
        'umbral':          umbral,
        'total':           len(productos_bajos),
        'productos_bajos': productos_bajos,
        'alerta_enviada':  alerta_enviada,
    }


def _enviar_alerta_stock(productos_bajos: list, umbral: int) -> bool:
    """Envía el correo de alerta de stock al primer administrador.

    Args:
        productos_bajos: lista de dicts con nombre, stock y categoría.
        umbral:          umbral mínimo configurado.

    Returns:
        True si el correo se envió; False si falló (se registra en el log).
    """
    from configuracion.models import ConfiguracionERP   # import local

    config = ConfiguracionERP.get_instance()
    fecha  = timezone.localtime().strftime('%d/%m/%Y %H:%M')

    contexto = {
        'productos_bajos': productos_bajos,
        'total_productos': len(productos_bajos),
        'umbral':          umbral,
        'fecha':           fecha,
        'url_admin':       _url_absoluta('admin:productos_producto_changelist'),
        'config':          config,
    }

    asunto = (
        f'[ALERTA] {len(productos_bajos)} producto(s) con stock < {umbral}'
    )
    texto_plano = render_to_string('emails/alerta_stock.txt',  contexto)
    html_body   = render_to_string('emails/alerta_stock.html', contexto)

    _admin_nombre, admin_correo = settings.ADMINS[0]

    mensaje = EmailMultiAlternatives(
        subject    = asunto,
        body       = texto_plano,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [admin_correo],
    )
    mensaje.attach_alternative(html_body, 'text/html')

    try:
        mensaje.send()
    except Exception as exc:
        logger.error(f'[stock_bajo] Error al enviar alerta: {exc}')
        return False

    logger.info(
        f'[stock_bajo] Alerta enviada a {admin_correo}. '
        f'{len(productos_bajos)} productos.'
    )
    return True
