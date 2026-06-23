# 📓 Bitácora del Proyecto — SENA GDF Sistema de Gestión

Registro cronológico del desarrollo, decisiones técnicas e iteraciones del sistema.

---

## Iteración 1 — Estructura base del proyecto

**Objetivo:** Levantar el proyecto Django con autenticación básica.

### Decisiones tomadas:
- Se eligió Django como framework por su ORM robusto, sistema de autenticación nativo y facilidad para manejar migraciones.
- Se extendió `AbstractUser` en lugar de usar el modelo nativo para poder agregar los campos `documento` y `rol` sin perder compatibilidad con el sistema de autenticación de Django.
- Se usó **SQLite** para desarrollo por su simplicidad (sin necesidad de configurar un servidor de BD).

### Archivos creados:
- `website/models.py` → modelos `Usuario` y `LogAuditoria`
- `website/views.py` → vistas de login, register, logout
- `website/templates/login.html` → UI de autenticación

---

## Iteración 2 — Seguridad multicapa

**Objetivo:** Implementar un sistema de defensa en profundidad.

### Decisiones tomadas:
- **Capa 2 (Rate Limiting):** Se creó un middleware personalizado (`RateLimitMiddleware`) en lugar de usar librerías de terceros como `django-ratelimit`, para mantener el proyecto con el mínimo de dependencias externas y tener control total sobre la lógica.
- **Capa 3 (XSS):** Se implementó `html.escape()` manualmente en cada input en lugar de depender únicamente del auto-escape de Django Templates, para proteger también los datos en la capa de vista antes de llegar al ORM.
- Se definieron **expresiones regulares** estrictas y centralizadas (REGEX_DOCUMENTO, REGEX_NOMBRES, REGEX_EMAIL, REGEX_PASSWORD) para evitar duplicación de lógica de validación.

### Archivos creados/modificados:
- `website/middleware.py` → `RateLimitMiddleware`
- `website/views.py` → función `sanitizar()` + patrones REGEX

---

## Iteración 3 — Panel de administración y CRUD

**Objetivo:** Construir el dashboard del administrador con gestión completa de usuarios.

### Decisiones tomadas:
- Se implementó **paginación del lado del servidor** con `django.core.paginator` (5 usuarios por página) en lugar de cargar toda la tabla al frontend, para garantizar rendimiento con grandes volúmenes de datos.
- El eliminado de usuarios usa `@require_POST` para que la acción destructiva no pueda ejecutarse con una petición GET (protección CSRF adicional).
- Se agregó una validación que impide que un administrador elimine su propia cuenta, retornando un error de forma controlada.

### Archivos creados/modificados:
- `website/views.py` → vistas `admin_dashboard`, `gestion_usuarios`, `user_delete`, `edit_user`
- `website/templates/admin_dashboard.html`
- `website/templates/gestion_usuarios.html`
- `website/templates/edit_user.html`

---

## Iteración 4 — Auditoría y logs

**Objetivo:** Registrar automáticamente todas las acciones sensibles del sistema.

### Decisiones tomadas:
- Se creó el modelo `LogAuditoria` con `ForeignKey` a `Usuario` usando `on_delete=models.SET_NULL` para preservar los logs históricos incluso si el usuario es eliminado del sistema.
- Los logs incluyen la **dirección IP del cliente**, con soporte para proxies y balanceadores de carga (lectura del header `HTTP_X_FORWARDED_FOR`).
- Se centralizó el registro en la función helper `registrar_log()` para garantizar consistencia en todos los eventos.

### Acciones auditadas:
- `LOGIN` / `LOGOUT` → Autenticación
- `REGISTRO` → Creación de usuarios
- `EDICION` → Modificación de datos
- `ELIMINACION` → Borrado de usuarios
- `REPORTE` → Exportación de datos

---

## Iteración 5 — División y modularización de vistas

**Objetivo:** Separar las secciones del panel admin en rutas y templates independientes.

### Problema resuelto:
El `admin_dashboard.html` era monolítico: contenía la tabla de usuarios, los logs y la bienvenida en un solo archivo, lo que dificultaba el mantenimiento.

### Decisión:
Se dividió en 3 vistas/templates independientes con rutas propias:

| Vista              | URL                         | Template                    |
|--------------------|-----------------------------|-----------------------------|
| `admin_dashboard`  | `/admin-dashboard/`         | `admin_dashboard.html`      |
| `gestion_usuarios` | `/admin-dashboard/usuarios/`| `gestion_usuarios.html`     |
| `logs_auditoria`   | `/admin-dashboard/logs/`    | `logs_auditoria.html`       |

---

## Iteración 6 — Exportación de reportes

**Objetivo:** Permitir al administrador descargar datos en formatos estándar de oficina.

### Decisiones tomadas:
- **CSV → Excel:** Se descartó exportar CSV (aunque es más simple) porque Excel no siempre reconoce el encoding UTF-8 y mostraba caracteres corruptos con tildes y eñes. La solución con `openpyxl` genera archivos `.xlsx` nativos con estilos, fuentes y bordes reales.
- **PDF:** Se eligió `ReportLab` sobre alternativas como `WeasyPrint` o `xhtml2pdf` por su mejor soporte en entornos Windows y su rendimiento superior al no depender de un motor de renderizado HTML.
- Los archivos se generan **en memoria** (sin escribir al disco del servidor), usando el `HttpResponse` directamente como buffer, lo que es más eficiente y seguro.
- Todos los reportes quedan registrados en el log de auditoría con la acción `REPORTE`.

---

## Iteración 7 — Diseño responsivo

**Objetivo:** Garantizar usabilidad en dispositivos móviles y tablets.

### Decisiones tomadas:
- **Menú hamburguesa:** Se implementó con CSS puro (transiciones sobre los `span`) + JavaScript mínimo (toggle de clase `.open`), sin depender de Bootstrap JS ni jQuery.
- **Tablas:** Se envolvieron en un contenedor `.table-wrapper` con `overflow-x: auto` para dar scroll horizontal en pantallas pequeñas, sin alterar el diseño de las tablas en desktop.
- **Breakpoints:** Se definieron 2 puntos de quiebre:
  - `≤ 900px` → Tablet: se oculta el navbar y aparece la hamburguesa.
  - `≤ 600px` → Móvil: layout en columna, elementos apilados.
- El formulario de login también se adapta en móvil: se oculta el panel de registro animado para simplificar la experiencia.

---

## Iteración 8 — Módulo del Aprendiz

**Objetivo:** Dar una experiencia útil al rol de Aprendiz dentro del sistema.

### Funcionalidades implementadas:
- **Panel de aprendiz** (`apprentice_dashboard.html`): pantalla de bienvenida con acceso a sus funciones.
- **Perfil propio** (`perfil_aprendiz.html`): el aprendiz puede actualizar sus datos básicos (nombre, apellidos, email). Los cambios quedan registrados en auditoría.
- **Cambio de contraseña**: formulario con validación de contraseña actual + nueva contraseña segura (REGEX_PASSWORD). Al cambiar la contraseña, la sesión se cierra automáticamente por seguridad.

---

## Resumen Final — Métricas del Proyecto

| Métrica                     | Valor                    |
|-----------------------------|--------------------------|
| Líneas de código (Python)   | ~470 (views.py)          |
| Líneas de CSS               | ~1000 (styles.css)       |
| Templates HTML              | 13 archivos              |
| Endpoints                   | 11 rutas                 |
| Modelos Django              | 2 (Usuario, LogAuditoria)|
| Capas de seguridad          | 4                        |
| Librerías externas usadas   | 3 (openpyxl, reportlab, pillow) |
| Breakpoints responsivos     | 2 (900px, 600px)         |
