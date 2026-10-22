# Ficha de Sistematización — Espiral 3
## ERP Django · Espiral E3: CRUD Web y Autenticación

| Campo | Contenido |
|---|---|
| **Número de espiral** | 3 |
| **Nombre del ciclo** | CRUD Web y Autenticación |
| **Semanas** | W07 – W09 |
| **Fecha de inicio** | ___/___/_____ |
| **Fecha de cierre** | ___/___/_____ |
| **Responsable** | [Nombre del estudiante] |
| **Asesor** | MC. Román Fernando López González |

## 1. Objetivo del ciclo
Implementar la interfaz web completa del ERP con vistas de lectura
y escritura, formularios validados, autenticación mediante allauth
y control de acceso por rol (RBAC) con 3 grupos de usuarios.

## 2. Tareas realizadas

| # | Tarea | Estado | Semana |
|---|---|---|---|
| 1 | ListView + DetailView × 4 entidades | ✅ | W07 |
| 2 | 8 templates lista + detalle Fable 5 | ✅ | W07 |
| 3 | select_related anti-N+1 | ✅ | W07 |
| 4 | forms.py × 4 apps (ModelForm) | ✅ | W08 |
| 5 | Create/Update/Delete × 3 entidades | ✅ | W08 |
| 6 | crear_venta (función) | ✅ | W08 |
| 7 | messages flash en CRUD | ✅ | W08 |
| 8 | django-allauth instalado | ✅ | W09 |
| 9 | Templates login/signup Fable 5 | ✅ | W09 |
| 10 | Management command crear_grupos | ✅ | W09 |
| 11 | PermissionRequiredMixin en Delete | ✅ | W09 |
| 12 | @login_required + @permission_required | ✅ | W09 |
| 13 | 10 tests RBAC | ✅ | W09 |

## 3. Evidencias
- URL pública: https://erp-django-utec.onrender.com
- Login funcional: /accounts/login/
- Tests: Ran 100 tests → OK
- Grupos: Gerente / Vendedor / Almacén en /admin/

## 4. Criterios de aceptación

| Criterio | Estado |
|---|---|
| GET /productos/ sin login → solo lectura | ✅ |
| GET /productos/eliminar/ sin permiso → 403 | ✅ |
| Gerente → acceso completo | ✅ |
| Vendedor → solo ventas y consulta | ✅ |
| 100 tests acumulados OK | ✅ |

## 5. Problemas encontrados
(completar durante la sesión)

## 6. Lecciones aprendidas
1.
2.
3.

## 7. Tiempo total invertido

| Categoría | Horas |
|---|---|
| Diseño | |
| Implementación | |
| Pruebas | |
| Documentación | |
| **Total Espiral 3** | |