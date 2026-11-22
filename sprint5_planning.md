## Sprint 5 — Estado final W18

| HU | Historia | Estado | Pts |
|---|---|---|---|
| HU-E6-01 | Infraestructura Celery+Redis funcional | ✅ Completada | 3 |
| HU-E6-02 | Tareas sin bloquear HTTP | ✅ Completada | 2 |
| HU-E6-03 | Correo de confirmación post-pago | ✅ Completada | 5 |
| HU-E6-04 | Correo de alerta de stock bajo | ✅ Completada | 3 |
| HU-E6-05 | Reporte diario de ventas a las 8 AM | ✅ Completada | 3 |
| HU-E6-06 | Monitorear tareas con Flower | ✅ Completada | 2 |
| **Total** | | | **18/18** |

## Sprint Backlog — actualización W18

| Tarea | Estado |
|---|---|
| reporte_ventas_diario: annotate + Sum(F('cantidad') * F('precio_unitario')) | ✅ W18 |
| Top 5 incluye compras en línea (Pedido.items_snapshot) | ✅ W18 |
| Templates reporte_ventas.html + .txt (KPIs + tabla) | ✅ W18 |
| CELERY_BEAT_SCHEDULE: reporte crontab(hour=8, minute=0) + stock timedelta(hours=1) | ✅ W18 |
| Hora configurable REPORTE_DIARIO_HORA (Render: 10:00 para pruebas) | ✅ W18 |
| Beat embebido en el worker de Render (--beat, CELERY_EMBEDDED_BEAT=1) | ✅ W18 |
| Fix kombu 5.7.0 → 5.3.7 (VersionMismatch con redis 5.0.1) | ✅ W18 |
| Acción admin "Enviar correo de confirmación" (pagados sin correo) | ✅ W18 |
| Suite completa en verde | ✅ W18 |

## Hito M6 — ALCANZADO ✅
- Worker: embebido en el contenedor web de Render (`--pool=solo`)
- Beat: embebido en el worker (`--beat`), una sola instancia
- Correo: enviar_confirmacion_pedido → solo desde el webhook, idempotente
- Alerta: verificar_stock_bajo → cada hora, correo al admin
- Reporte: crontab(hour=8, minute=0) → 8:00 AM hora de México
  (configurable con REPORTE_DIARIO_HORA)
- Tests: Ran 171 tests → OK (2 skipped: PDF requiere GTK, corre en Docker/Render)
- Fecha: 20/Noviembre/2026

### Observaciones de verificación (2026-11-20)
- Laboratorio sin Docker Desktop: Redis, worker, Beat y Flower solo
  existen en Render; localmente todo corre en modo EAGER.
- En Render el correo no llegaba por `kombu==5.7.0` + `redis==5.0.1`
  (VersionMismatch). Corregido; confirmar en los Logs tras el despliegue.
- Render Free se duerme sin tráfico: Beat solo dispara si el servicio
  está despierto (ping externo cada 10 min).
- Flower (HU-E6-06) está instalado (`flower==2.0.1`), pero no se expone
  en Render Free: en producción se monitorea con los Logs del worker.
