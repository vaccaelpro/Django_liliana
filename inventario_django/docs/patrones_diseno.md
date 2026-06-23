# 📚 Patrones de Diseño — SENA GDF Sistema de Gestión

Documentación de los patrones de diseño de software identificados e implementados en el proyecto.

---

## 1. Patrón MTV (Model-Template-View) — Arquitectura Principal

Django implementa una variante del clásico **MVC** llamada **MTV**:

| Capa       | Responsabilidad                                  | Archivo en el proyecto          |
|------------|--------------------------------------------------|---------------------------------|
| **Model**  | Define la estructura de datos y la lógica de negocio | `website/models.py`         |
| **Template** | Presenta los datos al usuario (HTML)           | `website/templates/*.html`      |
| **View**   | Procesa peticiones, aplica reglas y devuelve respuestas | `website/views.py`       |

```
Request HTTP → urls.py (Router) → View → Model (DB) → Template → Response HTTP
```

---

## 2. Patrón Decorator — Control de Acceso

Se usa el patrón **Decorator** de Python para proteger vistas sin modificar su lógica interna.

```python
# views.py — Aplicación de decoradores anidados
@login_required(login_url='login')          # Decorator 1: verifica sesión activa
@user_passes_test(es_administrador, login_url='login')  # Decorator 2: verifica rol
def gestion_usuarios(request):
    ...
```

**Beneficio:** La lógica de autorización está completamente separada de la lógica de negocio. Agregar nuevas restricciones solo requiere añadir un nuevo decorator.

---

## 3. Patrón Middleware (Chain of Responsibility) — Rate Limiting

El `RateLimitMiddleware` implementa el patrón **Chain of Responsibility**: cada middleware procesa la petición y decide si la pasa al siguiente eslabón o la detiene.

```python
# middleware.py
class RateLimitMiddleware:
    def __call__(self, request):
        # Si supera el límite → corta la cadena y responde con 429
        if intentos >= self.LIMITE:
            return HttpResponse("Demasiados intentos.", status=429)
        
        # Si no → pasa la petición al siguiente middleware/vista
        return self.get_response(request)
```

**Cadena de middlewares en settings.py:**
```
Request → SecurityMiddleware → SessionMiddleware → RateLimitMiddleware → View
```

---

## 4. Patrón Strategy — Exportación de Reportes

Las funciones de exportación implementan el patrón **Strategy**: el mismo algoritmo (obtener datos → estructurar → devolver archivo) se ejecuta con diferentes estrategias de formato.

| Estrategia         | Función            | Librería     | Formato Salida |
|--------------------|--------------------|--------------|----------------|
| ExcelStrategy      | `export_users_excel` | openpyxl   | `.xlsx`        |
| ExcelStrategy      | `export_logs_excel`  | openpyxl   | `.xlsx`        |
| PDFStrategy        | `export_users_pdf`   | ReportLab  | `.pdf`         |
| PDFStrategy        | `export_logs_pdf`    | ReportLab  | `.pdf`         |

```python
# Misma interfaz, diferente estrategia de serialización:
def export_users_excel(request):   # Estrategia: openpyxl workbook
    ...
    wb.save(response)

def export_users_pdf(request):     # Estrategia: ReportLab document
    ...
    doc.build(elements)
```

---

## 5. Patrón Observer (implícito) — Auditoría de Logs

La función `registrar_log()` actúa como un **Observer** que reacciona ante eventos del sistema sin acoplar la lógica del evento al almacenamiento del log.

```python
# views.py — Helper de auditoría (Observer)
def registrar_log(usuario, accion, detalle, request):
    """Registra acciones de auditoría con IP del cliente."""
    LogAuditoria.objects.create(
        usuario=usuario, accion=accion, detalle=detalle, ip=ip
    )

# Llamado desde cualquier evento relevante:
registrar_log(user, 'LOGIN', f'Inicio de sesión: {user.documento}', request)
registrar_log(request.user, 'ELIMINACION', f'Usuario eliminado: {user.documento}', request)
registrar_log(request.user, 'REPORTE', 'Exportó listado a Excel', request)
```

**Eventos observados:** LOGIN, LOGOUT, REGISTRO, EDICION, ELIMINACION, REPORTE.

---

## 6. Patrón Template Method — Validación de Formularios

La función `sanitizar()` y los patrones REGEX definen un **Template Method** reutilizable para validar cualquier campo de entrada:

```python
# views.py — Método plantilla de validación
def sanitizar(valor):
    return html.escape(str(valor).strip()) if valor else ''

# Patrones reutilizables en toda la aplicación
REGEX_DOCUMENTO = re.compile(r'^\d{5,12}$')
REGEX_NOMBRES   = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]{2,50}$')
REGEX_EMAIL     = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$')
REGEX_PASSWORD  = re.compile(r'^(?=.*[A-Z])(?=.*\d).{8,}$')
```

---

## 7. Principio DRY (Don't Repeat Yourself) — Componentes Reutilizables

Se aplica el principio **DRY** mediante la inclusión de componentes compartidos en Django Templates:

```html
<!-- Reutilizado en TODOS los templates del dashboard -->
{% include 'navbar.html' %}
```

El `navbar.html` contiene:
- Lógica de roles (admin vs aprendiz)
- Menú hamburguesa responsivo
- Script de auto-cierre de alertas
- Script del toggle del menú móvil

---

## 8. Defense in Depth — Seguridad por Capas

Patrón de seguridad que aplica múltiples barreras independientes:

```
┌─────────────────────────────────────────────────────┐
│  CAPA 1: Autenticación (@login_required)            │
│  ┌───────────────────────────────────────────────┐  │
│  │  CAPA 2: Rate Limiting (RateLimitMiddleware)  │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  CAPA 3: Sanitización XSS (html.escape) │  │  │
│  │  │  ┌───────────────────────────────────┐  │  │  │
│  │  │  │  CAPA 4: Validación REGEX         │  │  │  │
│  │  │  │  ┌─────────────────────────────┐  │  │  │  │
│  │  │  │  │  LÓGICA DE NEGOCIO          │  │  │  │  │
│  │  │  │  └─────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```
