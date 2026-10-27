========================================================================
ASISTEC — Sistema Inteligente de Registro de Asistencia Estudiantil
========================================================================

1. DESCRIPCION DEL PROYECTO
ASISTEC es una aplicacion web academica desarrollada con Python (Flask), HTML5,
CSS3 y MySQL (XAMPP). Su proposito es sistematizar y facilitar el registro,
consulta, analisis estadistico e impresion de reportes de asistencia estudiantil,
ofreciendo acceso diferenciado para Docentes y Coordinadores.

2. REQUISITOS DEL SISTEMA
- Python 3.10 o superior (con Flask y mysql-connector-python instalados).
- XAMPP instalado (con Apache y MySQL).
- Servidor MySQL activo en localhost:3306.
- Navegador web Google Chrome.

3. ESTRUCTURA ORGANIZADA DEL PROYECTO
ASISTEC/
│
├── html/                         -> Paginas y plantillas web
│   ├── login.html                -> Inicio de sesion
│   ├── docente.html              -> Panel principal del Docente
│   ├── coordinador.html          -> Panel principal del Coordinador
│   ├── registrar_asistencia.html -> Formulario de toma de asistencia
│   ├── consultar_asistencia.html -> Consulta con filtros dinamicos
│   ├── estadisticas.html         -> Metricas, resumenes y porcentajes
│   └── reporte.html              -> Reporte formal e impresion
│
├── css/                          -> Diseno visual
│   └── style.css                 -> Hoja de estilos globales y de impresion
│
├── bd/                           -> Base de datos relacional
│   └── asistec.sql               -> Respaldo SQL completo para restauracion
│
├── app.py                        -> Servidor web y rutas principales en Flask
├── conexion.py                   -> Modulo de conexion con MySQL
└── README.txt                    -> Documentacion y guia de instalacion/entrega

4. CONFIGURACION DE LA BASE DE DATOS
- Nombre de la base de datos: asistec
- Servidor: localhost (127.0.0.1)
- Puerto: 3306
- Usuario: root
- Contrasena: (vacia por defecto en XAMPP)

5. GUIA PASO A PASO PARA RESTAURAR LA BASE DE DATOS
Si se instala el proyecto en un computador nuevo o se desea restaurar la base de datos:
1. Abrir el panel de control de XAMPP.
2. Iniciar el servicio de MySQL (presionar "Start").
3. Abrir Google Chrome e ingresar a phpMyAdmin:
   http://localhost/phpmyadmin
4. En el menu izquierdo o superior, hacer clic en "Nueva" / "New".
5. Escribir como nombre de base de datos: asistec (con cotejamiento utf8mb4_general_ci) y presionar "Crear".
6. Hacer clic en la base de datos "asistec" creada y entrar a la pestana "Importar" / "Import".
7. Hacer clic en "Seleccionar archivo" y elegir el archivo:
   bd/asistec.sql
8. Bajar hasta el final de la pagina y presionar "Importar" / "Continuar".
9. Verificar que aparezcan las tablas: usuarios, estudiantes, docentes, grado, grupo, registroasistencia, etc.

6. INSTRUCCIONES DE EJECUCION
Paso 1: Verificar que MySQL este activo en XAMPP.
Paso 2: Abrir una terminal (PowerShell o CMD) en la carpeta del proyecto ASISTEC.
Paso 3: Ejecutar el comando:
        python app.py
Paso 4: Abrir Google Chrome e ingresar exactamente a:
        http://localhost:5000

7. USUARIOS DE PRUEBA REGISTRADOS EN LA BASE DE DATOS
------------------------------------------------------------------------
Rol           | Usuario     | Contrasena | Descripcion de Permisos
------------------------------------------------------------------------
Docente       | docente1    | 1234       | Acceso a registrar asistencia,
              |             |            | consultar historial propio, ver
              |             |            | metricas y generar su reporte.
------------------------------------------------------------------------
Coordinador   | coordinador | admin123   | Acceso a consultas generales,
              |             |            | metricas institucionales y
              |             |            | reporte general de toda la sede.
------------------------------------------------------------------------

8. FUNCIONALIDADES DEL SISTEMA
- Autenticacion con control de acceso por roles (Docente y Coordinador).
- Registro de asistencia con estados (Presente, Ausente, Tarde) y proteccion anti-duplicados.
- Consulta de historial con filtros por fecha, grado, grupo y estado.
- Metricas y estadisticas automaticas con porcentajes seguros y graficos visuales CSS.
- Reporte formal de asistencia con metadatos y boton de impresion limpia en Google Chrome.
- Cierre de sesion seguro y proteccion de todas las rutas internas.

9. GUIA PARA LA PRESENTACION ACADEMICA ANTE EL EVALUADOR
1. Explicar el objetivo del proyecto: modernizar el control de asistencia en las aulas.
2. Mostrar la base de datos "asistec" en phpMyAdmin.
3. Iniciar sesion como Docente (docente1 / 1234) en http://localhost:5000.
4. Demostrar el registro de asistencia seleccionando Grado 10 / Grupo A.
5. Demostrar la consulta y aplicacion de filtros en tiempo real.
6. Demostrar el modulo de estadisticas y porcentajes.
7. Demostrar el reporte formal y presionar "Imprimir reporte" en Chrome.
8. Cerrar sesion e ingresar como Coordinador (coordinador / admin123) mostrando la vision institucional.
9. Demostrar la seguridad intentando acceder a una URL interna sin sesion.
10. Concluir explicando que el sistema es ligero, 100% funcional y seguro.
========================================================================
