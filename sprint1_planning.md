# Sprint 1 Planning — ERP Django
## Semanas W04–W06 · Espiral 2: Modelado de Datos y ORM

**Sprint Goal:**
Al finalizar el Sprint 1, el ERP tendrá un esquema de base de datos
completo implementado en Django, con 8 entidades, relaciones verificadas,
panel admin funcional y una suite de ≥ 15 pruebas de modelo pasando.

**Duración:** W04 (diseño) · W05 (implementación) · W06 (validación + M2)

---

## HUs seleccionadas del Product Backlog

| ID | Historia de Usuario | Puntos | Semana |
|---|---|---|---|
| HU-E2-01 | Como dev, quiero un diagrama ER aprobado para tener el plano del ERP | 3 | W04 |
| HU-E2-02 | Como admin, quiero registrar clientes con nombre, correo y teléfono | 2 | W05 |
| HU-E2-03 | Como admin, quiero registrar proveedores con contacto y correo | 2 | W05 |
| HU-E2-04 | Como admin, quiero registrar categorías para clasificar productos | 1 | W05 |
| HU-E2-05 | Como admin, quiero registrar productos con precio, stock y categoría | 3 | W05 |
| HU-E2-06 | Como admin, quiero registrar ventas con líneas de detalle y total | 5 | W05 |
| HU-E2-07 | Como dev, quiero 15+ tests de modelo para garantizar la integridad | 3 | W06 |
| HU-E2-08 | Como admin, quiero ver todos los modelos en el panel admin con Jazzmin | 2 | W06 |

**Total de puntos del Sprint 1:** 21 puntos

---

## Sprint Backlog — Tareas técnicas

| Tarea | Semana | Estado |
|---|---|---|
| Diseñar diagrama ER (8 entidades) | W04 | ⏳ |
| Normalizar a 3FN y documentar decisiones | W04 | ⏳ |
| Obtener aprobación del asesor | W04 | ⏳ |
| Implementar models.py × 5 apps | W05 | ⏳ |
| Ejecutar makemigrations + migrate | W05 | ⏳ |
| Registrar modelos en admin.py | W05 | ⏳ |
| Agregar validators a campos críticos | W06 | ⏳ |
| Escribir tests/test_models.py (≥ 15 tests) | W06 | ⏳ |
| Instalar y configurar django-jazzmin | W06 | ⏳ |

---

## Definición de Terminado (DoD) — Sprint 1

- Diagrama ER aprobado formalmente por el asesor (firma en ficha)
- `python manage.py showmigrations` → `[X] 0001_initial` en cada app
- `/admin/` muestra las 8 entidades correctamente
- `python manage.py test tests.test_models` → ≥ 15 tests PASSED
- Precio negativo en Producto → `ValidationError`
- Correo duplicado en Cliente → `IntegrityError`
- `fichas/espiral_02_modelos.md` completa
