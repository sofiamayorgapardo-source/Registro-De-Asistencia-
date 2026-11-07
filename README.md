# ASISTEC — Sistema Inteligente de Registro de Asistencia Estudiantil

ASISTEC es una solución web académica diseñada para modernizar, agilizar y centralizar el control de asistencia, seguimiento a inasistencias y gestión estudiantil en instituciones educativas. Proporciona una interfaz intuitiva con roles de acceso diferenciados para **Docentes**, **Coordinadores** y **Rectoría**.

---

## 🚀 Características Principales

- **Gestión por Roles:**
  - **Docente:** Registro y consulta de asistencia diaria en asignaturas y grupos autorizados, control de justificaciones de inasistencia.
  - **Coordinación:** Administración académica integral, aprobación/activación de docentes, importación y exportación masiva de matrícula, reportes globales.
  - **Rectoría:** Supervisión institucional en modo consulta y seguimiento analítico de estadísticas.
- **Seguridad Integrada:**
  - Almacenamiento criptográfico de contraseñas mediante Werkzeug (`scrypt`/`pbkdf2`).
  - Protección activa contra ataques CSRF (Cross-Site Request Forgery) en todos los formularios.
  - Cookies de sesión seguras (`HttpOnly`, `SameSite=Lax`, `Secure` en HTTPS).
  - Validación de autorización en servidor (prevención de manipulaciones en peticiones GET y POST).
- **Control de Matrícula:**
  - Exportación de listados de matrícula en formato CSV estándar.
  - Importación masiva desde archivos `.csv` y `.xlsx` (Excel) con previsualización de datos.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.10+ / Flask 3.x
- **Servidor WSGI de Producción:** Gunicorn
- **Base de Datos:** MySQL / MariaDB (18 tablas relacionales)
- **Frontend:** HTML5, CSS3 institucional y JavaScript nativo
- **Procesamiento de Archivos:** `csv`, `openpyxl` (hojas de cálculo)
- **Seguridad:** Werkzeug Security, Secrets

---

## 📋 Requisitos del Sistema

- **Python:** Versión 3.10 o superior.
- **Base de Datos:** MySQL 8.0+ o MariaDB 10.4+ (vía XAMPP en desarrollo local o Aiven en la nube).
- **Gestor de Paquetes:** `pip`.

---

## 📁 Estructura del Proyecto

```text
ASISTEC/
├── bd/
│   └── asistec_estructura.sql   # Esquema oficial DDL (18 tablas) y catálogos iniciales
├── css/
│   ├── escudo.png               # Escudo e identidad visual
│   └── style.css                # Estilos visuales institucionales
├── docs/                        # Documentación técnica y pedagógica del proyecto
├── html/                        # Plantillas Jinja2 de la interfaz de usuario
│   ├── login.html
│   ├── docente.html
│   ├── coordinador.html
│   ├── rectoria.html
│   ├── registrar_asistencia.html
│   ├── consultar_asistencia.html
│   ├── registro_inasistencia.html
│   ├── gestion_estudiantes.html
│   ├── estudiante_formulario.html
│   ├── importar_estudiantes.html
│   ├── estadisticas.html
│   ├── reporte.html
│   └── crear_cuenta.html
├── .env.example                 # Plantilla de variables de entorno (desarrollo y nube)
├── .gitignore                   # Exclusiones de Git (seguridad y archivos temporales)
├── app.py                       # Aplicación principal Flask y controladores de ruta
├── conexion.py                  # Módulo de conexión a MySQL (XAMPP local / Nube con SSL)
├── Procfile                     # Configuración de arranque para Render (Gunicorn)
├── README.md                    # Documentación del repositorio
└── requirements.txt             # Dependencias de Python requeridas
```

---

## ⚙️ Instalación y Configuración Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/sofiamayorgapardo-source/Registro-De-Asistencia-.git
cd Registro-De-Asistencia-
```

### 2. Crear y activar un entorno virtual (recomendado)
- **En Windows:**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos MySQL con XAMPP

1. Iniciar el servicio **MySQL** desde el Panel de Control de XAMPP.
2. Abrir **phpMyAdmin** en el navegador (`http://localhost/phpmyadmin`) o la consola de MySQL.
3. Crear la base de datos:
   ```sql
   CREATE DATABASE asistec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
4. Importar el archivo de estructura oficial ubicado en [`bd/asistec_estructura.sql`](bd/asistec_estructura.sql):
   - Desde la pestaña **Importar** de phpMyAdmin seleccionando el archivo.
   - O por línea de comandos:
     ```bash
     mysql -u root -p asistec < bd/asistec_estructura.sql
     ```
   *Nota:* Este archivo creará las 18 tablas requeridas e insertará los catálogos académicos iniciales (grados, grupos, asignaturas y sedes).

### 5. Configurar Variables de Entorno (Opcional en Local)

El sistema cuenta con valores predeterminados para desarrollo local (`localhost:3306`, usuario `root`, base `asistec`). Si deseas personalizar la configuración:

1. Copia la plantilla `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Modifica los parámetros en tu archivo `.env` según tu entorno.

### 6. Ejecutar la Aplicación en Modo Local

```bash
python app.py
```

Abre tu navegador web e ingresa a:
👉 **`http://localhost:5000`**

---

## ☁️ Preparación para Despliegue en Render y Aiven

El proyecto está 100% preparado para ser alojado en la nube:

- **Plataforma Web:** [Render](https://render.com)
  - **Tipo de Servicio:** Web Service (Python 3).
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `gunicorn app:app` (definido en el `Procfile`).
  - **Puerto:** Render asigna automáticamente el puerto mediante la variable `PORT`.
- **Base de Datos:** [Aiven for MySQL](https://aiven.io) u otro proveedor compatible con MySQL.
  - Conexión segura TLS/SSL mediante las variables de entorno correspondientes.

### Variables de Entorno para Producción

En el panel de control de Render (sección **Environment Variables**), configura los siguientes parámetros:

| Variable | Descripción | Ejemplo / Valor |
| :--- | :--- | :--- |
| `FLASK_ENV` | Modo de ejecución de Flask | `production` |
| `SECRET_KEY` | Clave criptográfica para firmas de sesión | *(Cadena aleatoria de 64 caracteres)* |
| `DB_HOST` | Host o endpoint del servidor MySQL | `mysql-xxxx-asistec.aivencloud.com` |
| `DB_PORT` | Puerto de conexión MySQL | `12345` |
| `DB_USER` | Usuario de la base de datos | `avnadmin` |
| `DB_PASSWORD` | Contraseña del usuario | *(Contraseña provista por Aiven)* |
| `DB_NAME` | Nombre de la base de datos | `defaultdb` o `asistec` |
| `DB_SSL_MODE` | Exigencia de cifrado SSL/TLS | `REQUIRED` |

---

## 🔒 Buenas Prácticas de Seguridad y Privacidad

- El archivo `.env` está estrictamente ignorado por `.gitignore` para no exponer contraseñas en Git.
- El repositorio no contiene información privada ni datos sensibles de estudiantes o acudientes.
- Los respaldos con datos personales locales (`asistec_backup.sql`) están excluidos del control de versiones.

---

## 📄 Licencia y Derechos

Proyecto desarrollado para fines pedagógicos e institucionales. Todos los derechos reservados © 2026 ASISTEC.
