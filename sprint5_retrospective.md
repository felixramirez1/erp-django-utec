# Sprint 5 Retrospective — ERP Django
## Semanas W16–W18 · Espiral 6: Celery e Integraciones

**Fecha:** 20/11/2026

## ¿Qué funcionó bien? (Keep)
1. El campo `correo_enviado` en `Pedido` resolvió los duplicados (reintentos
   de Stripe y de Celery) sin un sistema externo de idempotencia.
2. `@override_settings(EMAIL_BACKEND=locmem)` hizo triviales los tests de
   correo: `mail.outbox` captura todo sin enviar nada.
3. Modo EAGER sin `REDIS_URL`: el laboratorio sin Docker Desktop puede
   desarrollar y probar todas las tareas sin Redis ni worker.
4. El webhook como ÚNICO disparador del correo, con `try/except`: si Redis
   falla, el pago queda registrado y Stripe recibe 200.
5. Worker y Beat embebidos en el contenedor web: Celery funciona en el
   plan gratuito de Render (sin Background Workers).

## ¿Qué mejorar? (Improve)
1. **Dependencias:** `pip freeze` subió `kombu` a 5.7.0, que exige
   `redis>=6.1`, con `redis==5.0.1` fijo. En producción ninguna tarea
   llegaba a Redis y en el laboratorio no se veía (EAGER no usa Redis).
   Se fijó `kombu==5.3.7` y se agregó `tests/test_w18_dependencias.py`.
2. **Variables de entorno:** valores capturados en el campo equivocado
   (`CELERY_EMBEDDED_BEAT=10:00`, `DEFAULT_FROM_EMAIL` = Reply-To en vez
   del From verificado). Revisar la tabla de variables antes de desplegar.
3. **Render Free se duerme:** Beat no dispara mientras el servicio duerme;
   se necesita un ping externo cada 10 min.
4. **Pruebas antiguas desactualizadas:** 11 fallas heredadas de W01–W12
   (rutas cambiadas en W07, mensajes en español, WeasyPrint sin GTK en
   Windows, ficha E1 faltante). Corregidas en este cierre.

## Acción de mejora (Kaizen) para Sprint 6
> "En el Sprint 6 no regeneraré `requirements.txt` con `pip freeze`:
>  agregaré solo la dependencia nueva y correré `pip check` y la prueba de
>  compatibilidad kombu↔redis antes de cada push. Y pre-calcularé los KPIs
>  del Dashboard con `annotate` desde el principio."

## Velocidad del Sprint 5

| HU | Pts plan. | Pts ent. |
|---|---|---|
| HU-E6-01 Infraestructura Celery+Redis | 3 | 3 |
| HU-E6-02 Tareas sin bloquear HTTP | 2 | 2 |
| HU-E6-03 Correo confirmación post-pago | 5 | 5 |
| HU-E6-04 Alerta stock bajo | 3 | 3 |
| HU-E6-05 Reporte diario 8 AM | 3 | 3 |
| HU-E6-06 Monitorear con Flower | 2 | 2 |
| **Total** | **18** | **18** |

**Velocidad Sprint 5:** 18 puntos
**Velocidad acumulada (S0–S5):** 123 puntos
**Tests al cierre:** 171 (OK, 2 skipped por GTK en Windows)
