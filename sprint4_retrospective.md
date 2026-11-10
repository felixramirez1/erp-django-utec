# Sprint 4 Retrospective — ERP Django
## Semanas W13–W15 · Espiral 5: E-commerce y Pagos

**Fecha:** ___/___/_____

## ¿Qué funcionó bien? (Keep)
1. items_snapshot en el Pedido resolvió elegantemente el problema
   de recuperar los items del carrito después de que la sesión
   fue limpiada.
2. La expresión F() garantizó que el stock nunca quede en negativo
   con múltiples webhooks simultáneos.
3. unittest.mock.patch permitió testear el webhook sin claves reales.

## ¿Qué mejorar? (Improve)
1. El template de checkout podría mostrar un loader más visible
   durante el procesamiento de pago.
2. Documentar el flujo de webhooks en el diagrama de arquitectura.

## Acción de mejora (Kaizen) para Sprint 5
> "En el Sprint 5 (Celery), crearé primero el test que verifica
>  que el correo se envía ANTES de implementar la tarea asíncrona."

## Velocidad del Sprint 4

| HU | Pts plan. | Pts ent. |
|---|---|---|
| HU-E5-01 Catálogo sin registro | 2 | 2 |
| HU-E5-02 Filtrar por categoría/precio | 3 | 3 |
| HU-E5-03 Agregar al carrito | 3 | 3 |
| HU-E5-04 Ver contenido del carrito | 2 | 2 |
| HU-E5-05 Checkout con datos del cliente | 3 | 3 |
| HU-E5-06 Pago con Stripe sandbox | 5 | 5 |
| HU-E5-07 Confirmar pago vía webhook | 5 | 5 |
| HU-E5-08 Descontar stock al confirmar | 3 | 3 |
| **Total** | **26** | **26** |

**Velocidad Sprint 4:** 26 puntos
**Velocidad acumulada (S0–S4):** 105 puntos
