# Sprint 4 Planning — ERP Django
## Semanas W13–W15 · Espiral 5: E-commerce y Pagos

**Sprint Goal:**
Al finalizar el Sprint 4, el ERP tendrá catálogo filtrable,
carrito de compras y pago completo con Stripe sandbox,
actualizando automáticamente el estado del pedido.

## HUs seleccionadas

| ID | Historia | Puntos | Semana |
|---|---|---|---|
| HU-E5-01 | Como cliente, quiero ver el catálogo sin registrarme | 2 | W13 |
| HU-E5-02 | Como cliente, quiero filtrar productos por categoría y precio | 3 | W13 |
| HU-E5-03 | Como cliente, quiero agregar productos a mi carrito | 3 | W13 |
| HU-E5-04 | Como cliente, quiero ver el contenido de mi carrito | 2 | W13 |
| HU-E5-05 | Como cliente, quiero proceder al pago con mis datos | 3 | W14 |
| HU-E5-06 | Como cliente, quiero pagar con tarjeta (Stripe sandbox) | 5 | W14 |
| HU-E5-07 | Como sistema, quiero confirmar el pago vía webhook | 5 | W15 |
| HU-E5-08 | Como admin, quiero que el stock se descuente al confirmar | 3 | W15 |

**Total Sprint 4:** 26 puntos

## DoD — Sprint 4
- GET /catalogo/ → 200 sin autenticación con lista de productos
- Filtrar por categoría → solo productos de esa categoría
- Agregar producto al carrito → contador en navbar se incrementa
- Tarjeta de prueba Stripe 4242... → pedido cambia a "pagado"
- Webhook verifica firma → stock se descuenta
- python manage.py test → ≥ 131 tests OK

## Sprint Backlog — actualización W13

| Tarea | Estado |
|---|---|
| App catalogo + django-filter | ✅ W13 |
| ProductoFilter (nombre/categoría/precio) | ✅ W13 |
| CatalogoView pública con paginación | ✅ W13 |
| Carrito en sesión (agregar/remover/actualizar/vaciar) | ✅ W13 |
| Context processor carrito_info | ✅ W13 |
| Template catalogo.html con tarjetas | ✅ W13 |
| Template carrito.html con tabla | ✅ W13 |
| Contador carrito en navbar base.html | ✅ W13 |
| 8 tests de e-commerce | ✅ W13 |
| Checkout con Stripe sandbox | ⏳ W14 |
| Webhooks y estados de pedido | ⏳ W15 |