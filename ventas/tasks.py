# ventas/tasks.py
"""Tareas asíncronas de la app ventas — W17 + W18.

W16: estructura base (solo log).
W17: envío real de correos con django-anymail + SendGrid.
W18: tareas programadas con Celery Beat (reporte diario de ventas).

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
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
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


# ── W17: confirmación de pedido ───────────────────────────────────────────

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


# ── W17: alerta de stock bajo ─────────────────────────────────────────────

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


# ── W18: reporte diario (Celery Beat) ─────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=2,
    name='ventas.reporte_ventas_diario',
)
def reporte_ventas_diario(self) -> dict:
    """Genera y envía el reporte diario de ventas al administrador.

    Se ejecuta automáticamente todos los días a la hora de
    settings.REPORTE_DIARIO_HORA (default 08:00, hora de México)
    mediante Celery Beat (configurado en CELERY_BEAT_SCHEDULE).

    Cálculos realizados en SQL (no en Python) para máxima eficiencia:
        - Total de pedidos pagados hoy
        - Total facturado (suma de total_pagado)
        - Top 5 productos por ingreso del día

    Returns:
        dict con total_pedidos, total_facturado y top_productos.
    """
    from configuracion.models import ConfiguracionERP      # import local
    from ventas.models        import DetalleVenta, Pedido  # import local

    hoy    = timezone.localdate()
    config = ConfiguracionERP.get_instance()

    # ── 1. KPIs del día ───────────────────────────────────────────────
    pedidos_hoy = Pedido.objects.filter(
        fecha_pedido__date=hoy,
        estado='pagado',
    )
    total_pedidos   = pedidos_hoy.count()
    total_facturado = pedidos_hoy.aggregate(
        total=Sum('total_pagado')
    )['total'] or Decimal('0.00')

    # ── 2. Top 5 productos por ingreso del día ─────────────────────────
    # Dos fuentes: ventas internas (DetalleVenta) y compras de la tienda
    # en línea (Pedido.items_snapshot). El checkout NO crea Venta, así
    # que sin la segunda fuente las compras en línea nunca aparecían.
    acumulado = {}   # nombre → {'unidades': int, 'ingreso': Decimal}

    internas = (
        DetalleVenta.objects
        .filter(venta__fecha__date=hoy)
        .values(nombre=F('producto__nombre'))
        .annotate(
            unidades=Sum('cantidad'),
            ingreso=Sum(
                ExpressionWrapper(
                    F('cantidad') * F('precio_unitario'),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            ),
        )
    )
    for fila in internas:
        dato = acumulado.setdefault(
            fila['nombre'], {'unidades': 0, 'ingreso': Decimal('0.00')}
        )
        dato['unidades'] += fila['unidades'] or 0
        dato['ingreso']  += fila['ingreso'] or Decimal('0.00')

    for pedido in pedidos_hoy.only('items_snapshot'):
        for item in _items_con_subtotal(pedido.items_snapshot):
            dato = acumulado.setdefault(
                item.get('nombre', '¿?'),
                {'unidades': 0, 'ingreso': Decimal('0.00')},
            )
            dato['unidades'] += item['cantidad']
            dato['ingreso']  += item['subtotal']

    top_productos = sorted(
        (
            {
                'nombre':   nombre,
                'unidades': d['unidades'],
                'ingreso':  str(d['ingreso'].quantize(Decimal('0.01'))),
            }
            for nombre, d in acumulado.items()
        ),
        key=lambda x: Decimal(x['ingreso']),
        reverse=True,
    )[:5]

    logger.info(
        f'[reporte_diario] {hoy}: {total_pedidos} pedidos, '
        f'${total_facturado} facturados, '
        f'{len(top_productos)} productos top.'
    )

    # ── 3. Enviar correo al admin si está configurado ──────────────────
    if settings.ADMINS:
        _enviar_reporte_ventas(
            hoy, total_pedidos, total_facturado, top_productos, config
        )

    return {
        'fecha':           str(hoy),
        'total_pedidos':   total_pedidos,
        'total_facturado': str(total_facturado),
        'top_productos':   top_productos,
    }


def _enviar_reporte_ventas(
    fecha, total_pedidos, total_facturado, top_productos, config
) -> None:
    """Envía el reporte diario al primer administrador configurado.

    Args:
        fecha:           Objeto date del día reportado.
        total_pedidos:   Número de pedidos pagados.
        total_facturado: Decimal con la suma total.
        top_productos:   Lista de dicts con nombre, unidades, ingreso.
        config:          Instancia de ConfiguracionERP.
    """
    url_admin = _url_absoluta('admin:ventas_pedido_changelist')
    fecha_str = fecha.strftime('%d/%m/%Y')

    contexto = {
        'fecha':           fecha_str,
        'config':          config,
        'total_pedidos':   total_pedidos,
        'total_facturado': total_facturado,
        'top_productos':   top_productos,
        'url_admin':       url_admin,
        'hora_programada': settings.REPORTE_DIARIO_HORA,
    }

    asunto      = f'Reporte de ventas del {fecha_str} — {config.nombre_empresa}'
    texto_plano = render_to_string('emails/reporte_ventas.txt',  contexto)
    html_body   = render_to_string('emails/reporte_ventas.html', contexto)

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
        logger.info(f'[reporte_diario] Reporte enviado a {admin_correo}.')
    except Exception as exc:
        logger.error(f'[reporte_diario] Error al enviar reporte: {exc}')