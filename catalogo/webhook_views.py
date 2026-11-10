# catalogo/webhook_views.py
"""Endpoint de webhook para recibir eventos de Stripe — W15.

Verificación de seguridad:
    Stripe firma cada evento con STRIPE_WEBHOOK_SECRET.
    stripe.Webhook.construct_event() verifica la firma.
    Si la firma es inválida → 400 (Stripe no reintenta).
    Si la firma es válida → procesar el evento → 200.

Eventos manejados:
    payment_intent.succeeded     → Pedido.estado = 'pagado'
                                    Descontar stock de productos
    payment_intent.payment_failed → Pedido.estado = 'cancelado'
"""
import logging

import stripe
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from productos.models import Producto
from ventas.models    import Pedido

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request) -> HttpResponse:
    """Recibe y procesa eventos de Stripe.

    Flujo:
        1. Leer payload crudo (bytes) y header de firma.
        2. Verificar firma con STRIPE_WEBHOOK_SECRET.
        3. Despachar al handler del tipo de evento.
        4. Retornar 200 (éxito) o 400 (firma inválida).

    Args:
        request: HttpRequest con cuerpo raw y header Stripe-Signature.

    Returns:
        HttpResponse: 200 si el evento fue procesado correctamente,
                      400 si la firma es inválida o el payload es inválido.
    """
    payload    = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    # ── 1. Verificar firma ─────────────────────────────────────────────────
    try:
        event = stripe.Webhook.construct_event(
            payload    = payload,
            sig_header = sig_header,
            secret     = settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        # Payload malformado (no es JSON válido)
        logger.warning('Webhook: payload inválido recibido.')
        return HttpResponse('Payload inválido.', status=400)
    except stripe.error.SignatureVerificationError:
        # Firma inválida — posible intento de falsificación
        logger.warning('Webhook: firma inválida — posible ataque.')
        return HttpResponse('Firma inválida.', status=400)

    # ── 2. Despachar por tipo de evento ────────────────────────────────────
    tipo = event['type']
    logger.info(f'Webhook recibido: {tipo}')

    if tipo == 'payment_intent.succeeded':
        _manejar_pago_exitoso(event['data']['object'])

    elif tipo == 'payment_intent.payment_failed':
        _manejar_pago_fallido(event['data']['object'])

    else:
        logger.debug(f'Evento ignorado: {tipo}')

    # Siempre retornar 200 para eventos que no necesitamos
    # (Stripe reintentará si recibe 4xx o 5xx)
    return HttpResponse(status=200)


# ── HANDLERS INTERNOS ──────────────────────────────────────────────────────

def _manejar_pago_exitoso(payment_intent: dict) -> None:
    """Procesa un pago confirmado por Stripe.

    Actualiza el Pedido a 'pagado' y descuenta el stock de productos.

    Args:
        payment_intent: objeto PaymentIntent del evento de Stripe.
    """
    pedido_id = _extraer_pedido_id(payment_intent)
    if pedido_id is None:
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Webhook: Pedido {pedido_id} no encontrado en BD.')
        return

    # Actualizar estado del pedido
    if pedido.estado != 'pagado':
        pedido.estado = 'pagado'
        pedido.save(update_fields=['estado'])
        logger.info(
            f'Pedido {pedido.numero_pedido} actualizado a "pagado".'
        )

        # Descontar stock de cada producto del snapshot
        _descontar_stock(pedido)
    else:
        logger.info(
            f'Pedido {pedido.numero_pedido} ya estaba pagado — '
            f'idempotente, sin cambios.'
        )


def _manejar_pago_fallido(payment_intent: dict) -> None:
    """Procesa un pago fallido o rechazado.

    Actualiza el Pedido a 'cancelado'.

    Args:
        payment_intent: objeto PaymentIntent del evento de Stripe.
    """
    pedido_id = _extraer_pedido_id(payment_intent)
    if pedido_id is None:
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Webhook: Pedido {pedido_id} no encontrado.')
        return

    if pedido.estado == 'pendiente':
        pedido.estado = 'cancelado'
        pedido.save(update_fields=['estado'])
        logger.info(
            f'Pedido {pedido.numero_pedido} cancelado por pago fallido.'
        )


def _extraer_pedido_id(payment_intent: dict) -> int | None:
    """Extrae el pedido_id del metadata del PaymentIntent.

    Args:
        payment_intent: objeto PaymentIntent de Stripe.

    Returns:
        int con el ID del pedido, o None si no está en el metadata.
    """
    metadata  = payment_intent.get('metadata', {})
    pedido_id = metadata.get('pedido_id')

    if not pedido_id:
        logger.warning(
            f'Webhook: PaymentIntent sin pedido_id en metadata. '
            f'ID de PaymentIntent: {payment_intent.get("id")}'
        )
        return None

    try:
        return int(pedido_id)
    except (ValueError, TypeError):
        logger.error(f'Webhook: pedido_id inválido: {pedido_id!r}')
        return None


def _descontar_stock(pedido: 'Pedido') -> None:
    """Descuenta el stock de los productos del pedido.

    Usa expresiones F() para actualizar el stock de forma atómica,
    evitando race conditions cuando múltiples webhooks llegan
    simultáneamente.

    Args:
        pedido: instancia de Pedido con items_snapshot cargado.
    """
    items = pedido.items_snapshot or []

    for item in items:
        producto_id = item.get('producto_id')
        cantidad    = int(item.get('cantidad', 0))

        if not producto_id or cantidad <= 0:
            continue

        # F('stock') - cantidad: actualización atómica en la BD
        # Evita leer el stock actual en Python (race condition)
        filas_actualizadas = Producto.objects.filter(
            pk=producto_id,
            stock__gte=cantidad    # solo si hay stock suficiente
        ).update(
            stock=F('stock') - cantidad
        )

        if filas_actualizadas:
            logger.info(
                f'Stock decrementado: Producto {producto_id} '
                f'- {cantidad} unidades.'
            )
        else:
            logger.warning(
                f'Producto {producto_id}: stock insuficiente para '
                f'decrementar {cantidad} unidades.'
            )