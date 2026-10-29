# Sprint 3 Planning — ERP Django
## Semanas W10–W12 · Espiral 4: API REST y Media

**Sprint Goal:**
Al finalizar el Sprint 3, el ERP expondrá una API REST completa
con autenticación por token, gestión de imágenes de productos
y generación de PDFs de facturas.

## HUs seleccionadas

| ID | Historia | Puntos | Semana |
|---|---|---|---|
| HU-E4-01 | Como dev externo, quiero listar productos via API sin auth | 2 | W10 |
| HU-E4-02 | Como dev, quiero crear productos via API con token | 3 | W10 |
| HU-E4-03 | Como dev, quiero API para clientes, proveedores y ventas | 3 | W10 |
| HU-E4-04 | Como admin, quiero subir imagen de producto | 3 | W11 |
| HU-E4-05 | Como dev, quiero que la imagen aparezca en la API | 2 | W11 |
| HU-E4-06 | Como cliente, quiero descargar la factura en PDF | 5 | W12 |
| HU-E4-07 | Como admin, quiero exportar inventario a Excel | 3 | W12 |

**Total Sprint 3:** 21 puntos

## DoD — Sprint 3
- GET /api/productos/ → JSON 200 sin autenticación
- POST /api/productos/ sin token → 403
- POST /api/productos/ con token válido → 201
- Imagen de producto visible en /media/
- GET /ventas/<id>/pdf/ → descarga PDF con líneas de detalle
- GET /productos/exportar-excel/ → archivo .xlsx descargable
- python manage.py test tests → ≥ 107 tests OK

## Sprint Backlog — actualización W10

| Tarea | Estado |
|---|---|
| rest_framework.authtoken instalado | ✅ W10 |
| Serializers × 5 entidades | ✅ W10 |
| ListCreateAPIView + RetrieveUpdateDestroyAPIView × 5 | ✅ W10 |
| api_urls.py × 4 apps + /api/ en core/urls.py | ✅ W10 |
| Token endpoint /api/auth/token/ | ✅ W10 |
| 7 tests APIClient pasando | ✅ W10 |
| ImageField + Pillow + MEDIA_ROOT | ⏳ W11 |
| django-storages + S3/MinIO | ⏳ W11 |
| Generación PDF WeasyPrint | ⏳ W12 |
| Exportación Excel openpyxl | ⏳ W12 |

## Sprint Backlog — actualización W11

| Tarea | Estado |
|---|---|
| Serializers + API Views + Token Auth | ✅ W10 |
| Pillow + filetype instalados | ✅ W11 |
| ImageField en Producto + migración 0002 | ✅ W11 |
| Validador custom (MIME + tamaño) | ✅ W11 |
| ProductoSerializer con imagen_url | ✅ W11 |
| ProductoForm con widget imagen | ✅ W11 |
| Templates crear/editar: enctype multipart | ✅ W11 |
| detalle.html muestra imagen | ✅ W11 |
| ProductoAdmin con preview de imagen | ✅ W11 |
| django-storages configurado para prod | ✅ W11 |
| 8 tests de media pasando | ✅ W11 |
| Generación PDF WeasyPrint | ⏳ W12 |
| Exportación Excel openpyxl | ⏳ W12 |