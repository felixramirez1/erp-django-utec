# Ficha de Sistematización — Espiral 6
## ERP Django · Espiral E6: Celery e Integraciones
## UTEC Celaya · Técnico en Programación (SEP 3061300006-23)

| Campo | Contenido |
|---|---|
| **Número de espiral** | 6 |
| **Nombre del ciclo** | Celery e Integraciones |
| **Semanas** | W16 – W18 |
| **Fecha de inicio** | ___/___/_____ |
| **Fecha de cierre** | 20/11/2026 |
| **Responsable** | [Nombre del estudiante] |
| **Asesor** | MC. Román Fernando López González |

---

## 1. Objetivo del ciclo

Implementar procesamiento asíncrono con Celery y Redis para:
correos transaccionales de confirmación de pedido, alertas de
stock bajo y reportes diarios automáticos vía Celery Beat, en un
entorno sin Docker Desktop (laboratorio en modo EAGER) y con
producción en el plan gratuito de Render.

---

## 2. Tareas realizadas

| # | Tarea | Estado | Semana |
|---|---|---|---|
| 1 | Celery 5.3.6 + redis 5.0.1 + flower 2.0.1 | ✅ | W16 |
| 2 | `core/celery.py` + `core/__init__.py` | ✅ | W16 |
| 3 | `CELERY_*` en settings: Redis si hay `REDIS_URL`, EAGER si no | ✅ | W16 |
| 4 | Worker embebido en `docker-entrypoint.sh` (`CELERY_EMBEDDED_WORKER=1`) | ✅ | W16 |
| 5 | Webhook `payment_intent.succeeded` como único disparador del correo | ✅ | W16 |
| 6 | `django-anymail[sendgrid]==10.3`; SendGrid en prod si hay API Key | ✅ | W17 |
| 7 | `Pedido.correo_enviado` + migración 0004 (idempotencia) | ✅ | W17 |
| 8 | Templates `confirmacion_pedido` y `alerta_stock` (.html + .txt) con `items_snapshot` | ✅ | W17 |
| 9 | `enviar_confirmacion_pedido`: correo real + idempotencia + retry | ✅ | W17 |
| 10 | `verificar_stock_bajo`: alerta al admin | ✅ | W17 |
| 11 | Templates `reporte_ventas` (.html + .txt) con KPIs y tabla | ✅ | W18 |
| 12 | `reporte_ventas_diario` con `annotate` + `Sum(F('cantidad') * F('precio_unitario'))` | ✅ | W18 |
| 13 | `CELERY_BEAT_SCHEDULE`: crontab(hour=8, minute=0) + timedelta(hours=1) | ✅ | W18 |
| 14 | Beat embebido en el worker de Render (`--beat`) | ✅ | W18 |
| 15 | Fix `kombu==5.3.7` (VersionMismatch con redis-py 5.0.1) | ✅ | W18 |
| 16 | Acción admin para reenviar confirmación de pagados sin correo | ✅ | W18 |

---

## 3. Evidencias

- Pruebas: `python manage.py test tests` → **Ran 171 tests — OK (skipped=2)**
  (los 2 omitidos generan PDF con WeasyPrint y requieren GTK: corren en Docker/Render)
- Pruebas de la espiral: `test_w16_celery` (9), `test_w17_correo` (12),
  `test_w18_beat` (10), `test_w18_dependencias` (2)
- Correo de confirmación: consola local `Resultado 1: ok` / `Resultado 2: skip`
- Logs de Render a verificar tras desplegar:
  - [ ] `Celery Beat embebido ACTIVADO (reporte diario HH:MM hora MX)`
  - [ ] `celery@... ready.` y `beat: Starting...` sin `VersionMismatch`
  - [ ] `Task ventas.enviar_confirmacion_pedido[...] succeeded ... 'estado': 'ok'`
  - [ ] `Scheduler: Sending due task reporte-ventas-diario-8am`
- [ ] Captura del correo recibido: `evidencias/espiral_06/correo_confirmacion.png`
- [ ] Captura del reporte diario: `evidencias/espiral_06/reporte_diario.png`

---

## 4. Criterios de aceptación

| Criterio | Estado |
|---|---|
| Worker procesa `enviar_confirmacion_pedido` | ✅ (EAGER local · Render tras fix kombu) |
| `correo_enviado=True` previene duplicados | ✅ |
| Alerta de stock enviada al admin | ✅ |
| `reporte_ventas_diario` en `CELERY_BEAT_SCHEDULE` | ✅ |
| `verificar_stock_bajo` en `CELERY_BEAT_SCHEDULE` | ✅ |
| 171 tests OK | ✅ |

---

## 5. Problemas encontrados

| Problema | Causa | Solución aplicada |
|---|---|---|
| Sin Docker Desktop en el laboratorio | Política del equipo | Modo EAGER sin `REDIS_URL`; Redis/worker solo en Render |
| Render Free sin Background Workers | Plan gratuito | Worker y Beat embebidos en el contenedor web |
| Webhook: `VersionMismatch: redis-py 6.1.0 or later` | `pip freeze` subió `kombu` a 5.7.0 | `kombu==5.3.7` + prueba de compatibilidad |
| Reporte de las 8:30 nunca llegó | Worker sin `--beat` y servicio dormido | `--beat` en el entrypoint + ping externo |
| Top de productos vacío | El checkout crea `Pedido`, no `Venta` | Top suma también `items_snapshot` |
| SendGrid 403 | `DEFAULT_FROM_EMAIL` ≠ remitente verificado | Usar el From del Single Sender |
| `requirements.txt` en UTF-16 | `pip freeze >` en PowerShell | Editar a mano / usar cmd |

---

## 6. Lecciones aprendidas

1. El modo EAGER es ideal para desarrollar, pero oculta los errores de
   conexión con el broker: hay que probar el transporte real o al menos
   la compatibilidad de versiones.
2. La idempotencia (`correo_enviado`) se diseña desde el modelo, no se
   agrega después.
3.

---

## 7. Tiempo total invertido

| Categoría | Horas |
|---|---|
| Diseño | |
| Implementación | |
| Pruebas | |
| Documentación | |
| **Total Espiral 6** | |
