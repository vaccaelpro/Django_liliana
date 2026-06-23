# 📐 Diagramas UML — SENA GDF Sistema de Gestión

Documentación técnica del sistema mediante diagramas UML representados en sintaxis **Mermaid**.

---

## 1. Diagrama de Clases (Modelos)

```mermaid
classDiagram
    class AbstractUser {
        +username: CharField
        +email: EmailField
        +first_name: CharField
        +last_name: CharField
        +password: CharField
        +is_active: BooleanField
        +date_joined: DateTimeField
    }

    class Usuario {
        +documento: CharField
        +rol: CharField
        +ROLES: tuple
        +get_rol_display() str
        +__str__() str
    }

    class LogAuditoria {
        +accion: CharField
        +detalle: TextField
        +ip: GenericIPAddressField
        +fecha: DateTimeField
        +ACCIONES: tuple
        +get_accion_display() str
        +__str__() str
    }

    AbstractUser <|-- Usuario : hereda
    Usuario "1" --> "0..*" LogAuditoria : genera
```

---

## 2. Diagrama de Casos de Uso

```mermaid
graph TD
    subgraph Actores
        ADMIN[👤 Administrador]
        APREND[👤 Aprendiz]
    end

    subgraph Sistema["Sistema SENA GDF"]
        UC1[Iniciar Sesión]
        UC2[Cerrar Sesión]
        UC3[Ver Dashboard]
        UC4[Gestionar Usuarios]
        UC4a[Crear Usuario]
        UC4b[Editar Usuario]
        UC4c[Eliminar Usuario]
        UC4d[Buscar Usuario]
        UC5[Ver Logs de Auditoría]
        UC6[Exportar Reporte Excel]
        UC7[Exportar Reporte PDF]
        UC8[Ver Perfil Propio]
        UC9[Cambiar Contraseña]
    end

    ADMIN --> UC1
    ADMIN --> UC2
    ADMIN --> UC3
    ADMIN --> UC4
    UC4 --> UC4a
    UC4 --> UC4b
    UC4 --> UC4c
    UC4 --> UC4d
    ADMIN --> UC5
    ADMIN --> UC6
    ADMIN --> UC7
    ADMIN --> UC8

    APREND --> UC1
    APREND --> UC2
    APREND --> UC3
    APREND --> UC8
    APREND --> UC9
```

---

## 3. Diagrama de Flujo — Autenticación (Login)

```mermaid
flowchart TD
    A([Usuario accede a /Login/]) --> B{¿Ya autenticado?}
    B -- Sí --> C{¿Rol?}
    C -- ADMINISTRADOR --> D[Redirige a /admin-dashboard/]
    C -- APRENDIZ --> E[Redirige a /apprentice-dashboard/]
    B -- No --> F[Muestra formulario de login]
    F --> G[Usuario envía POST]
    G --> H[RateLimitMiddleware\n¿Más de 5 intentos en 60s?]
    H -- Sí --> I[HTTP 429 - Too Many Requests]
    H -- No --> J[Sanitizar: html.escape en documento]
    J --> K{¿Documento válido\n5-12 dígitos?}
    K -- No --> L[Mensaje de error]
    K -- Sí --> M{¿Contraseña\n≥ 8 caracteres?}
    M -- No --> L
    M -- Sí --> N{¿Existe usuario\ncon ese documento?}
    N -- No --> L
    N -- Sí --> O[authenticate usuario]
    O --> P{¿Credenciales\ncorrectas?}
    P -- No --> L
    P -- Sí --> Q[login + registrar_log LOGIN]
    Q --> C
```

---

## 4. Diagrama de Flujo — Registro de Usuario

```mermaid
flowchart TD
    A([Admin envía formulario de registro]) --> B[RateLimitMiddleware]
    B --> C[Sanitizar todos los campos]
    C --> D{¿Validaciones REGEX\npasan?}
    D -- No --> E[Mensaje de error y redirige]
    D -- Sí --> F{¿Rol válido?}
    F -- No --> E
    F -- Sí --> G{¿Documento único\nen BD?}
    G -- No --> E
    G -- Sí --> H{¿Email único\nen BD?}
    H -- No --> E
    H -- Sí --> I[create_user en DB]
    I --> J[registrar_log REGISTRO]
    J --> K[Mensaje de éxito]
    K --> L([Redirige a login])
```

---

## 5. Diagrama de Secuencia — Exportación de Reporte

```mermaid
sequenceDiagram
    actor Admin
    participant Browser
    participant View
    participant DB
    participant Archivo

    Admin->>Browser: Click "Exportar Excel/PDF"
    Browser->>View: GET /admin-dashboard/usuarios/exportar-excel/
    View->>View: @login_required + @user_passes_test
    View->>DB: Usuario.objects.all()
    DB-->>View: QuerySet de usuarios
    View->>Archivo: Crear workbook/documento
    Archivo-->>View: Buffer en memoria
    View->>DB: registrar_log('REPORTE', ...)
    View-->>Browser: HttpResponse con Content-Disposition: attachment
    Browser-->>Admin: Descarga del archivo
```

---

## 6. Diagrama de Componentes — Arquitectura del Sistema

```mermaid
graph LR
    subgraph Cliente["Cliente (Browser)"]
        HTML[HTML5 + CSS3]
        FA[Font Awesome]
        BS[Bootstrap 5]
    end

    subgraph Django["Servidor Django"]
        MW[RateLimitMiddleware]
        URLS[urls.py - Router]
        VIEWS[views.py - Lógica]
        MODELS[models.py - ORM]
        TEMPLATES[Templates HTML]
    end

    subgraph Librerias["Librerías Python"]
        OPENPYXL[openpyxl\nExcel .xlsx]
        REPORTLAB[ReportLab\nPDF]
    end

    subgraph BD["Base de Datos"]
        SQLITE[(SQLite / MySQL)]
    end

    Cliente <-->|HTTP| MW
    MW --> URLS
    URLS --> VIEWS
    VIEWS --> MODELS
    MODELS <--> SQLITE
    VIEWS --> TEMPLATES
    TEMPLATES --> Cliente
    VIEWS --> OPENPYXL
    VIEWS --> REPORTLAB
    OPENPYXL -->|.xlsx| Cliente
    REPORTLAB -->|.pdf| Cliente
```

---

## 7. Diagrama de Estados — Sesión de Usuario

```mermaid
stateDiagram-v2
    [*] --> Anonimo : Usuario accede al sistema

    Anonimo --> Autenticando : Envía credenciales
    Autenticando --> Bloqueado : Supera límite de intentos (429)
    Autenticando --> Anonimo : Credenciales incorrectas
    Autenticando --> SesionActiva : Autenticación exitosa

    SesionActiva --> VistaAdmin : Rol = ADMINISTRADOR
    SesionActiva --> VistaAprendiz : Rol = APRENDIZ

    VistaAdmin --> GestionUsuarios : Navega a /usuarios/
    VistaAdmin --> LogsAuditoria : Navega a /logs/
    VistaAdmin --> ExportaReporte : Descarga Excel o PDF

    VistaAprendiz --> PerfilAprendiz : Navega a /mi-perfil/
    VistaAprendiz --> CambiaPassword : Actualiza contraseña

    VistaAdmin --> Anonimo : Cierra sesión
    VistaAprendiz --> Anonimo : Cierra sesión
    Bloqueado --> Anonimo : Expira ventana de 60s
```
