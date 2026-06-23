# 🟢 SENA GDF — Sistema de Gestión y Control de Usuarios

> Sistema web de gestión interna desarrollado con **Django 5** para el SENA (Servicio Nacional de Aprendizaje de Colombia). Permite administrar usuarios, auditar actividad del sistema y exportar reportes institucionales.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Variables de Entorno](#-variables-de-entorno)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Roles y Permisos](#-roles-y-permisos)
- [Seguridad](#-seguridad)
- [Exportación de Reportes](#-exportación-de-reportes)
- [Créditos](#-créditos)

---

## ✅ Características

| Módulo                  | Descripción                                                    |
|-------------------------|----------------------------------------------------------------|
| 🔐 Autenticación         | Login/Registro con validación multicapa y sanitización XSS    |
| 👥 Gestión de Usuarios   | CRUD completo con paginación y búsqueda en tiempo real        |
| 📋 Logs de Auditoría     | Registro automático de todas las acciones críticas del sistema |
| 📊 Exportación Excel     | Genera archivos `.xlsx` estilizados con `openpyxl`            |
| 📄 Exportación PDF       | Genera reportes PDF institucionales con `ReportLab`           |
| 📱 Diseño Responsivo     | Interfaz adaptable a móvil, tablet y escritorio               |
| 🛡️ Rate Limiting         | Protección contra fuerza bruta (5 intentos / 60 seg por IP)  |

---

## 🛠 Tecnologías

### Backend
- **Python 3.13**
- **Django 5.0.14** — Framework principal
- **SQLite** (desarrollo) / **MySQL** (producción)
- **openpyxl 3.1.5** — Exportación a Excel
- **ReportLab 4.4** — Exportación a PDF

### Frontend
- **HTML5 + CSS3 Vanilla** — Sin frameworks adicionales
- **Bootstrap 5** — Grid y utilidades de layout
- **Font Awesome 6** — Iconografía
- **Google Fonts (Inter)** — Tipografía

---

## 🏗 Arquitectura

El sistema sigue el patrón **MTV (Model-Template-View)** de Django con separación de responsabilidades en 3 capas de seguridad:

```
Capa 1: Autenticación y autorización  → @login_required + @user_passes_test
Capa 2: Rate Limiting                 → RateLimitMiddleware (middleware.py)
Capa 3: Sanitización XSS             → html.escape() en todos los inputs
```

### Flujo de una petición:

```
Request → RateLimitMiddleware → View → Sanitización → Validación → Model → DB
                                                                  ↓
                                                            Template (HTML)
```

---

## 🚀 Instalación

### Requisitos previos
- Python 3.10 o superior
- pip
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd inventario_django

# 2. Crear y activar entorno virtual
python -m venv env

# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate

# 3. Instalar dependencias
pip install django openpyxl reportlab pillow

# 4. Aplicar migraciones
cd dcrm
python manage.py migrate

# 5. Crear superusuario administrador
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

El sistema estará disponible en: **http://127.0.0.1:8000/**

---

## 🔑 Variables de Entorno

Para producción, se recomienda configurar las siguientes variables en un archivo `.env`:

```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
DATABASE_URL=mysql://user:password@host:3306/db_name
```

---

## 📁 Estructura del Proyecto

```
inventario_django/
├── dcrm/                          # Directorio raíz de Django
│   ├── dcrm/                      # Configuración del proyecto
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── website/                   # Aplicación principal
│   │   ├── models.py              # Modelos: Usuario, LogAuditoria
│   │   ├── views.py               # Vistas: auth, CRUD, exportación
│   │   ├── urls.py                # Rutas de la aplicación
│   │   ├── middleware.py          # Rate Limiting middleware
│   │   ├── admin.py               # Configuración del admin de Django
│   │   └── templates/             # Plantillas HTML
│   │       ├── navbar.html        # Barra de navegación con menú hamburguesa
│   │       ├── login.html         # Pantalla de autenticación
│   │       ├── admin_dashboard.html
│   │       ├── gestion_usuarios.html
│   │       ├── logs_auditoria.html
│   │       ├── apprentice_dashboard.html
│   │       ├── perfil_aprendiz.html
│   │       ├── edit_user.html
│   │       ├── 404.html / 500.html
│   │       └── static/
│   │           └── css/
│   │               └── styles.css # Estilos globales + responsivos
│   └── manage.py
└── README.md
```

---

## 👥 Roles y Permisos

| Funcionalidad          | Administrador | Aprendiz |
|------------------------|:---:|:---:|
| Ver panel principal    | ✅  | ✅  |
| Gestionar usuarios     | ✅  | ❌  |
| Ver logs de auditoría  | ✅  | ❌  |
| Exportar a Excel       | ✅  | ❌  |
| Exportar a PDF         | ✅  | ❌  |
| Editar propio perfil   | ✅  | ✅  |
| Cambiar contraseña     | ❌  | ✅  |

---

## 🛡️ Seguridad

El sistema implementa un modelo de defensa en profundidad (**Defense in Depth**):

1. **Capa 1 — Autenticación y Autorización**
   - Uso de `@login_required` y `@user_passes_test` en cada vista protegida.
   - Redirección automática al login si la sesión no es válida.

2. **Capa 2 — Rate Limiting**
   - `RateLimitMiddleware` bloquea IPs que superen **5 intentos de login** en 60 segundos.
   - Responde con HTTP `429 Too Many Requests`.

3. **Capa 3 — Sanitización XSS**
   - Todos los inputs de usuario pasan por `html.escape()` antes de ser procesados.
   - Previene inyección de código HTML/JavaScript malicioso.

4. **Validaciones adicionales**
   - Regex estrictos para documento, nombres, email y contraseña.
   - Validación de unicidad de documento y correo antes de registrar.
   - Contraseñas hasheadas con el sistema nativo de Django (PBKDF2 + SHA256).

---

## 📊 Exportación de Reportes

### Excel (.xlsx) — `openpyxl`
- Cabeceras con color verde institucional SENA (`#2E8B57`), texto blanco en negrita.
- Todas las celdas con bordes finos y alineación automática.
- Columnas autoajustadas según el contenido.

### PDF — `ReportLab`
- Formato horizontal (Landscape) en tamaño Carta.
- Título del reporte en la parte superior.
- Tabla con cabeceras institucionales y filas con fondo alternado.

---

## 👨‍💻 Créditos

Desarrollado como proyecto académico para el **SENA — Centro de Gestión de Mercados, Logística y Tecnologías de la Información (CGMLTI)**.

- **Aprendiz:** Santiago
- **Tecnología:** Python / Django
- **Año:** 2026
