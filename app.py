# -*- coding: utf-8 -*-
import os
import sys
import unicodedata
import re
from datetime import datetime
import io
import csv
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash

directorio_actual = os.path.dirname(os.path.abspath(__file__))
sys.path.append(directorio_actual)

from conexion import obtener_conexion

app = Flask(
    __name__,
    template_folder=os.path.join(directorio_actual, "html"),
    static_folder=os.path.join(directorio_actual, "css"),
    static_url_path="/css"
)

# Cargar variables opcionales desde .env sin sobrescribir las variables de Render
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except Exception:
    pass

# Configuración de clave secreta segura desde variables de entorno
secret_key_env = os.environ.get('SECRET_KEY', '').strip()
if os.environ.get('RENDER'):
    if not secret_key_env:
        raise RuntimeError("La variable de entorno SECRET_KEY es obligatoria en producción (Render).")
    app.secret_key = secret_key_env
else:
    app.secret_key = secret_key_env or 'asistec_secret_key_2026_dev_fallback'

# Configuración de seguridad para cookies de sesión
app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=True if os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production' else False,
    PERMANENT_SESSION_LIFETIME=14400
)

# =========================================================================
# PROTECCIÓN CSRF (CROSS-SITE REQUEST FORGERY)
# =========================================================================

@app.before_request
def ensure_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(24)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=session.get('csrf_token', ''))

@app.before_request
def validate_csrf():
    if request.method == 'POST':
        sent_token = (
            request.form.get('csrf_token') or
            request.headers.get('X-CSRFToken') or
            request.headers.get('X-CSRF-Token')
        )
        expected_token = session.get('csrf_token')

        if request.endpoint == 'login' and not sent_token:
            return None

        if sent_token and expected_token and secrets.compare_digest(str(sent_token), str(expected_token)):
            return None

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'error': 'Token de seguridad CSRF inválido o expirado. Recarga la página.'}), 403

        if request.endpoint == 'login':
            return render_template('login.html', error="Token de seguridad inválido. Por favor recarga la página."), 403

        return render_template('login.html', error="Solicitud rechazada: Token de seguridad CSRF inválido o expirado. Inicia sesión nuevamente."), 403

# =========================================================================
# REGLAS ACADÉMICAS INSTITUCIONALES DE ASIGNATURAS POR GRADO Y MODALIDAD
# =========================================================================

# Asignaturas generales para todos los grados (1 a 11)
ASIGNATURAS_GENERALES = [
    'Tecnología e Informática',
    'Ciencias Naturales',
    'Química',
    'Inglés',
    'Matemáticas',
    'Lengua Castellana',
    'Educación Artística',
    'Educación Religiosa',
    'Educación Física',
    'Emprendimiento',
    'Ética y Valores',
    'Sociales'
]

# Asignaturas exclusivas de Grados 10 y 11
ASIGNATURAS_10_11 = [
    'Física',
    'Filosofía',
    'Ciencias Económicas y Políticas'
]

# Asignatura de secundaria media (Grados 8 y 9)
ASIGNATURA_CONTABILIDAD = 'Contabilidad'

# Orden oficial de presentación institucional de las 16 asignaturas
ORDEN_OFICIAL_ASIGNATURAS = [
    'Tecnología e Informática',
    'Ciencias Naturales',
    'Química',
    'Inglés',
    'Matemáticas',
    'Lengua Castellana',
    'Educación Artística',
    'Educación Religiosa',
    'Educación Física',
    'Emprendimiento',
    'Ética y Valores',
    'Sociales',
    'Física',
    'Filosofía',
    'Contabilidad',
    'Ciencias Económicas y Políticas'
]

MODALIDADES_TECNICAS = [
    'General',
    'Técnico Contable',
    'Técnico en Programación de Software'
]

JORNADAS_DISPONIBLES = [
    'Mañana',
    'Tarde',
    'Nocturna'
]

SEDES_DISPONIBLES = [
    'Sede Central',
    'San Francisco',
    'Secundino Porras',
    'Sede Picaleña',
    'Sede Arboleda',
    'Bellorizonte',
    'San Martín'
]

ID_ASIGNATURAS_BD = {
    1: 'Tecnología e Informática',
    2: 'Ciencias Naturales',
    3: 'Inglés',
    4: 'Matemáticas',
    5: 'Lengua Castellana',
    6: 'Química',
    7: 'Educación Artística',
    8: 'Educación Religiosa',
    9: 'Emprendimiento',
    10: 'Ética y Valores',
    11: 'Sociales',
    12: 'Física',
    13: 'Filosofía',
    14: 'Contabilidad',
    15: 'Ciencias Económicas y Políticas',
    16: 'Educación Física'
}

def normalizar_nombre_asignatura(nombre):
    if not nombre:
        return ''
    s = unicodedata.normalize('NFKD', str(nombre)).encode('ASCII', 'ignore').decode('utf-8').lower().strip()
    if 'tecnolog' in s or 'informat' in s:
        return 'tecnologia_e_informatica'
    if 'natural' in s:
        return 'ciencias_naturales'
    if 'quimic' in s:
        return 'quimica'
    if 'educ' in s and 'fisic' in s:
        return 'educacion_fisica'
    if 'fisic' in s:
        return 'fisica'
    if 'ingles' in s:
        return 'ingles'
    if 'matemat' in s:
        return 'matematicas'
    if 'castellana' in s or 'lengua' in s or 'lenguaje' in s:
        return 'lengua_castellana'
    if 'artistic' in s:
        return 'educacion_artistica'
    if 'religio' in s:
        return 'educacion_religiosa'
    if 'emprend' in s:
        return 'emprendimiento'
    if 'etic' in s or 'valor' in s:
        return 'etica_y_valores'
    if 'social' in s:
        return 'sociales'
    if 'filosof' in s:
        return 'filosofia'
    if 'contab' in s:
        return 'contabilidad'
    if 'econom' in s or 'politic' in s:
        return 'ciencias_economicas_y_politicas'
    return re.sub(r'[^a-z0-9]', '', s)

def normalizar_grado_num(grado):
    if grado is None:
        return None
    s = str(grado).strip().lower().replace('º', '').replace('°', '').replace('grado', '').strip()
    if 'transici' in s or s == '0':
        return 0
    try:
        val = int(s)
        if 0 <= val <= 11:
            return val
    except ValueError:
        pass
    return None

# =========================================================================
# GRUPOS ACADÉMICOS POR GRADO — ASIGNACIÓN ESTRICTA
# =========================================================================

GRUPOS_POR_GRADO = {
    '0': ['Transición'],
    'transicion': ['Transición'],
    'transición': ['Transición'],
    '1': ['1-1', '1-2'],
    '2': ['2-1', '2-2'],
    '3': ['3-1', '3-2'],
    '4': ['4-1', '4-2'],
    '5': ['5-1', '5-2', '5-3'],
    '6': ['6-1', '6-2', '6-3', '6-4', '6-5'],
    '7': ['7-1', '7-2', '7-3', '7-4', '7-5', '7-6'],
    '8': ['8-1', '8-2', '8-3', '8-4', '8-5', '8-6', '8-7'],
    '9': ['9-1', '9-2', '9-3', '9-4', '9-5'],
    '10': ['10-1', '10-2', '10-3', '10-4', '10-5', '10-6'],
    '11': ['11-1', '11-2', '11-3', '11-4', '11-5', '11-6'],
}

def obtener_grupos_validos(grado):
    if grado is None:
        return []
    s = str(grado).strip().lower().replace('grado', '').replace('º', '').replace('°', '').strip()
    if 'transici' in s or s == '0':
        return ['Transición']
    return GRUPOS_POR_GRADO.get(s, [])

def grupo_valido_para_grado(grado, grupo_id_o_nombre):
    if not grado or not grupo_id_o_nombre:
        return True
    validos = [v.lower() for v in obtener_grupos_validos(grado)]
    if not validos:
        return True
    g_str = str(grupo_id_o_nombre).strip().lower()
    for v in validos:
        if g_str == v or g_str == v.replace(' ', ''):
            return True
    if str(grupo_id_o_nombre).isdigit():
        conn = obtener_conexion()
        if conn and conn.is_connected():
            c = conn.cursor(dictionary=True)
            c.execute("SELECT Gru_NombreGrupo, Gru_Cod_Grado FROM grupo WHERE Gru_Codigo = %s;", (int(grupo_id_o_nombre),))
            row = c.fetchone()
            c.close()
            conn.close()
            if row:
                if row['Gru_NombreGrupo'].lower() in validos:
                    return True
                g_num = normalizar_grado_num(grado)
                if g_num is not None and row['Gru_Cod_Grado'] == g_num:
                    return True
        return False
    return False

def obtener_asignaturas_validas(grado, modalidad=None):
    """
    Reglas académicas institucionales:
    1. Grados 1 a 11 ven TODAS las asignaturas generales:
       - Tecnología e Informática
       - Ciencias Naturales
       - Química
       - Inglés
       - Matemáticas
       - Lengua Castellana
       - Educación Artística
       - Educación Religiosa
       - Emprendimiento
       - Ética y Valores
       - Sociales
    2. Física, Filosofía, Ciencias Económicas y Políticas:
       - SOLO Grados 10 y 11 (NO en grados 1 a 9).
    3. Contabilidad:
       - Grados 8 y 9: SÍ (regla general).
       - Grados 1 a 7: NO.
    4. Excepciones Grados 10 y 11:
       - Técnico Contable:
         * Contabilidad: SÍ
         * Tecnología e Informática: NO
         * Demás asignaturas del grado (Física, Filosofía, Ciencias Económicas y Políticas, y resto de generales): SÍ
       - Técnico en Programación de Software:
         * Contabilidad: NO
         * Tecnología e Informática: SÍ
         * Demás asignaturas del grado: SÍ
       - General / Normal:
         * Tecnología e Informática: SÍ
         * Contabilidad: NO
         * Demás asignaturas del grado: SÍ
    """
    g_num = normalizar_grado_num(grado)
    if g_num is None or g_num < 1 or g_num > 11:
        # Si no hay grado seleccionado, mostrar las 11 asignaturas generales por defecto en selectores
        return [m for m in ORDEN_OFICIAL_ASIGNATURAS if m in ASIGNATURAS_GENERALES]

    # 1. Grados 1 a 7: Exclusivamente las 11 materias generales
    if g_num <= 7:
        return [m for m in ORDEN_OFICIAL_ASIGNATURAS if m in ASIGNATURAS_GENERALES]

    # 2. Grados 8 y 9: Las 11 materias generales + Contabilidad
    if g_num in [8, 9]:
        permitidas = set(ASIGNATURAS_GENERALES) | {'Contabilidad'}
        return [m for m in ORDEN_OFICIAL_ASIGNATURAS if m in permitidas]

    # 3. Grados 10 y 11:
    if g_num in [10, 11]:
        mod = str(modalidad or '').strip().lower()
        es_contable = 'contable' in mod
        es_software = 'software' in mod or 'program' in mod

        if es_contable:
            # Técnico Contable: NO Tecnología e Informática, SÍ Contabilidad, SÍ Física, Filosofía, Cs. Económicas y Políticas
            permitidas = (set(ASIGNATURAS_GENERALES) - {'Tecnología e Informática'}) | {'Contabilidad', 'Física', 'Filosofía', 'Ciencias Económicas y Políticas'}
        elif es_software:
            # Técnico en Programación de Software: SÍ Tecnología e Informática, NO Contabilidad, SÍ Física, Filosofía, Cs. Económicas y Políticas
            permitidas = set(ASIGNATURAS_GENERALES) | {'Física', 'Filosofía', 'Ciencias Económicas y Políticas'}
        else:
            # General / Normal: SÍ Tecnología e Informática, NO Contabilidad, SÍ Física, Filosofía, Cs. Económicas y Políticas
            permitidas = set(ASIGNATURAS_GENERALES) | {'Física', 'Filosofía', 'Ciencias Económicas y Políticas'}

        return [m for m in ORDEN_OFICIAL_ASIGNATURAS if m in permitidas]

    return [m for m in ORDEN_OFICIAL_ASIGNATURAS if m in ASIGNATURAS_GENERALES]

def asignatura_valida(grado, modalidad, asignatura):
    if not asignatura:
        return False
    asig_str = str(asignatura).strip()
    if asig_str.isdigit():
        asig_str = ID_ASIGNATURAS_BD.get(int(asig_str), asig_str)
    
    norm_asig = normalizar_nombre_asignatura(asig_str)
    if not norm_asig:
        return False

    validas = obtener_asignaturas_validas(grado, modalidad)
    validas_norm = [normalizar_nombre_asignatura(v) for v in validas]
    return norm_asig in validas_norm

# =========================================================================
# RUTAS API JSON PARA DINAMISMO EN FRONTEND
# =========================================================================

# =========================================================================
# FUNCIÓN COMÚN CENTRALIZADA: OBTENER ESTUDIANTES POR GRADO Y GRUPO
# =========================================================================

def obtener_estudiantes_por_grado_grupo(grado, grupo, jornada=None, sede=None):
    """
    Obtiene la lista oficial de estudiantes desde MySQL según grado y grupo.
    Normaliza el grupo tanto si viene en nombre ('11-6') como en código ('116').
    Retorna lista de diccionarios ordenada por Est_Apellido ASC, Est_Nombre ASC.
    """
    if not grado or not grupo:
        return []

    grupo_id = str(grupo).strip()
    if grupo_id and not grupo_id.isdigit():
        c_norm = obtener_conexion()
        if c_norm and c_norm.is_connected():
            cur_n = c_norm.cursor(dictionary=True)
            cur_n.execute("SELECT Gru_Codigo FROM grupo WHERE Gru_NombreGrupo = %s LIMIT 1;", (grupo_id,))
            rg = cur_n.fetchone()
            cur_n.close()
            c_norm.close()
            if rg:
                grupo_id = str(rg['Gru_Codigo'])

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        sql = """
            SELECT e.Est_CodEstudiante, e.Est_Nombre, e.Est_Apellido, e.Est_Cod_Grado, e.Est_Cod_Grupo, e.Est_Cod_SedeEstudiantil, e.Est_Jornada, s.Sed_NomSede
            FROM estudiantes e
            LEFT JOIN sedes s ON e.Est_Cod_SedeEstudiantil = s.Sed_CodigoSede
            WHERE e.Est_Cod_Grado = %s AND e.Est_Cod_Grupo = %s
              AND (e.Est_Estado = 'Activo' OR e.Est_Estado IS NULL OR e.Est_Estado = '')
        """
        params = [grado, grupo_id]
        if jornada:
            if 'ma' in jornada.lower() and 'ana' in jornada.lower():
                sql += " AND (e.Est_Jornada LIKE %s OR e.Est_Jornada LIKE %s)"
                params.extend(['Mañana%', 'Ma%ana%'])
            else:
                sql += " AND e.Est_Jornada LIKE %s"
                params.append(f"{jornada}%")
        if sede:
            if str(sede).isdigit():
                sql += " AND e.Est_Cod_SedeEstudiantil = %s"
                params.append(int(sede))
            else:
                sql += " AND (s.Sed_NomSede LIKE %s OR %s LIKE CONCAT('%%', s.Sed_NomSede, '%%'))"
                params.extend([f"%{sede}%", sede])

        sql += " ORDER BY e.Est_Apellido ASC, e.Est_Nombre ASC;"
        cursor.execute(sql, tuple(params))
        filas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return filas
    except Exception as e:
        print(f"[ERROR obtener_estudiantes_por_grado_grupo]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return []

@app.route('/api/asignaturas_validas')
def api_asignaturas_validas():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    grado = request.args.get('grado', '')
    modalidad = request.args.get('modalidad', 'General')
    materias = obtener_asignaturas_validas(grado, modalidad)
    if session.get('rol') == 'docente':
        doc_info = obtener_info_academica_docente(session.get('id_docente'))
        if doc_info.get('todas_asignaturas'):
            materias = [m for m in materias if m in doc_info['todas_asignaturas']]
            if not materias:
                materias = doc_info['todas_asignaturas']

    
    conexion = obtener_conexion()
    items = []
    if conexion and conexion.is_connected():
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Asi_CodAsignatura, Asi_NomAsignatura FROM asignatura ORDER BY Asi_CodAsignatura;")
        filas = cursor.fetchall()
        cursor.close()
        conexion.close()
        for m in materias:
            cod = None
            m_norm = normalizar_nombre_asignatura(m)
            for f in filas:
                f_norm = normalizar_nombre_asignatura(f['Asi_NomAsignatura'])
                if f_norm == m_norm:
                    cod = f['Asi_CodAsignatura']
                    break
            items.append({'id': cod or m, 'nombre': m})
    else:
        items = [{'id': m, 'nombre': m} for m in materias]
    return jsonify(items)

@app.route('/api/grupos_validos')
def api_grupos_validos():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    grado = request.args.get('grado', '').strip()
    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return jsonify([])
    try:
        cursor = conexion.cursor(dictionary=True)
        gra_codigo = None
        if grado.isdigit() or grado == '0':
            gra_codigo = int(grado)
        elif grado:
            cursor.execute("SELECT Gra_Codigo FROM grado WHERE LOWER(Gra_NombreGrado) = LOWER(%s) OR LOWER(Gra_NombreGrado) LIKE %s;", (grado, f"%{grado}%"))
            f = cursor.fetchone()
            if f:
                gra_codigo = f['Gra_Codigo']

        if gra_codigo is not None:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (gra_codigo,))
            grupos = cursor.fetchall()
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
            grupos = cursor.fetchall()

        cursor.close()
        conexion.close()
        resultado = [{'id': g['Gru_Codigo'], 'nombre': g['Gru_NombreGrupo']} for g in grupos]
        return jsonify(resultado)
    except Exception as e:
        print(f"[ERROR api_grupos_validos]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return jsonify([])

@app.route('/api/estudiantes_validos')
def api_estudiantes_validos():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    grado = request.args.get('grado', '').strip()
    grupo = request.args.get('grupo', '').strip()
    jornada = request.args.get('jornada', '').strip()
    sede = request.args.get('sede', '').strip()

    filas = obtener_estudiantes_por_grado_grupo(grado, grupo, jornada, sede)
    resultado = []
    for f in filas:
        resultado.append({
            'id': f['Est_CodEstudiante'],
            'nombre': f['Est_Nombre'],
            'apellido': f['Est_Apellido'],
            'nombre_completo': f"{f['Est_Apellido']}, {f['Est_Nombre']}".strip()
        })
    return jsonify(resultado)

# =========================================================================
# RUTAS DE AUTENTICACIÓN Y ROLES
# =========================================================================

@app.route('/')
def inicio():
    if 'usuario' in session:
        if session.get('rol') == 'docente':
            return redirect(url_for('docente'))
        elif session.get('rol') == 'coordinador':
            return redirect(url_for('coordinador'))
        elif session.get('rol') == 'rectoria':
            return redirect(url_for('rectoria'))
    return redirect(url_for('login'))

def verificar_password(stored_password, provided_password):
    if not stored_password or not provided_password:
        return False
    if stored_password.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
        try:
            return check_password_hash(stored_password, provided_password)
        except Exception:
            return False
    return stored_password == provided_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()

        if not usuario or not password:
            return render_template('login.html', error="Por favor ingresa usuario y contraseña.")
        
        conexion = obtener_conexion()
        if conexion and conexion.is_connected():
            try:
                cursor = conexion.cursor(dictionary=True)
                sql = "SELECT id_usuario, usuario, password, rol, id_docente, nombre, estado FROM usuarios WHERE usuario = %s;"
                cursor.execute(sql, (usuario,))
                user = cursor.fetchone()

                if user and verificar_password(user['password'], password):
                    if user.get('estado') == 'Inactivo':
                        cursor.close()
                        conexion.close()
                        return render_template('login.html', error="Esta cuenta se encuentra inactiva o pendiente de activación. Contacte a Coordinación.")

                    # Migración transparente y segura a hash Werkzeug
                    if not str(user['password']).startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
                        try:
                            nuevo_hash = generate_password_hash(password)
                            cursor.execute("UPDATE usuarios SET password = %s WHERE id_usuario = %s;", (nuevo_hash, user['id_usuario']))
                            conexion.commit()
                        except Exception as e_mig:
                            print(f"[AVISO MIGRACION PASSWORD]: {e_mig}")

                    nombre_real = user.get('nombre')
                    if not nombre_real and user.get('id_docente'):
                        cursor.execute("SELECT Doc_Nombres, Doc_Apellidos FROM docentes WHERE Doc_CodDocentes = %s LIMIT 1;", (user['id_docente'],))
                        d_row = cursor.fetchone()
                        if d_row:
                            nombre_real = f"{d_row['Doc_Nombres']} {d_row['Doc_Apellidos']}".strip()

                    cursor.close()
                    conexion.close()

                    session['id_usuario'] = user['id_usuario']
                    session['usuario'] = user['usuario']
                    session['rol'] = user['rol']
                    session['id_docente'] = user['id_docente']
                    session['nombre'] = nombre_real or user['usuario']
                    session['area'] = obtener_area_docente(user['id_docente']) if user.get('id_docente') else ''

                    if user['rol'] == 'docente':
                        return redirect(url_for('docente'))
                    elif user['rol'] == 'coordinador':
                        return redirect(url_for('coordinador'))
                    elif user['rol'] == 'rectoria':
                        return redirect(url_for('rectoria'))
                    else:
                        session.clear()
                        return render_template('login.html', error="Rol no autorizado.")
                else:
                    cursor.close()
                    conexion.close()
                    return render_template('login.html', error="Usuario o contraseña incorrectos.")
            except Exception as e:
                print(f"[ERROR LOGIN]: {e}")
                if conexion and conexion.is_connected():
                    conexion.close()
                return render_template('login.html', error="Error al consultar credenciales.")
        else:
            return render_template('login.html', error="Error al conectar con MySQL en XAMPP.")

    if 'usuario' in session:
        if session.get('rol') == 'docente':
            return redirect(url_for('docente'))
        elif session.get('rol') == 'coordinador':
            return redirect(url_for('coordinador'))
        elif session.get('rol') == 'rectoria':
            return redirect(url_for('rectoria'))
            
    return render_template('login.html')

@app.route('/crear_cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    conexion = obtener_conexion()
    asignaturas = []
    if conexion and conexion.is_connected():
        try:
            cur = conexion.cursor(dictionary=True)
            cur.execute("SELECT Asi_CodAsignatura, Asi_NomAsignatura FROM asignatura ORDER BY Asi_CodAsignatura;")
            asignaturas = cur.fetchall()
            cur.close()
        except Exception as e:
            print(f"[ERROR ASIGNATURAS]: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    if request.method == 'POST':
        tipo_usuario = request.form.get('tipo_usuario', '').strip().lower()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()
        confirmar_password = request.form.get('confirmar_password', '').strip()
        clave_autorizacion = request.form.get('clave_autorizacion', '').strip()

        # Datos académicos para Docente
        area_principal = request.form.get('area_principal', '').strip()
        areas_secundarias_raw = request.form.getlist('areas_secundarias')
        if not areas_secundarias_raw and request.form.get('area_secundaria'):
            v = request.form.get('area_secundaria').strip()
            if v and v not in ['', 'ninguna', '0']:
                areas_secundarias_raw = [v]

        # Filtrar duplicados, vacíos y evitar que el área principal se repita como secundaria
        areas_secundarias = []
        for a in areas_secundarias_raw:
            a_str = str(a).strip()
            if a_str and a_str not in ['', 'ninguna', '0'] and a_str != str(area_principal):
                if a_str not in areas_secundarias:
                    areas_secundarias.append(a_str)

        es_jefe = request.form.get('es_jefe', 'no').strip().lower()
        area_jefe = request.form.get('area_jefe', '').strip()

        form_data = {
            'tipo_usuario': tipo_usuario,
            'nombre_completo': nombre_completo,
            'usuario': usuario,
            'area_principal': area_principal,
            'areas_secundarias': areas_secundarias,
            'es_jefe': es_jefe,
            'area_jefe': area_jefe
        }

        # Validación estricta de tipo de usuario permitido (lista blanca)
        if tipo_usuario not in ('docente', 'coordinador'):
            return render_template('crear_cuenta.html',
                                   error="Tipo de usuario no válido.",
                                   asignaturas=asignaturas,
                                   form_data=form_data), 400

        # Validaciones comunes obligatorias
        if not tipo_usuario or not nombre_completo or not usuario or not password or not confirmar_password:
            return render_template('crear_cuenta.html', 
                                   error="Por favor completa todos los campos obligatorios.", 
                                   asignaturas=asignaturas, 
                                   form_data=form_data)

        if password != confirmar_password:
            return render_template('crear_cuenta.html', 
                                   error="Las contraseñas no coinciden.", 
                                   asignaturas=asignaturas, 
                                   form_data=form_data)

        # Validaciones para Docente
        if tipo_usuario == 'docente':
            if not area_principal:
                return render_template('crear_cuenta.html', 
                                       error="Debes seleccionar el área principal del docente.", 
                                       asignaturas=asignaturas, 
                                       form_data=form_data)
            
            # Validación de límite máximo de 5 áreas secundarias
            if len(areas_secundarias_raw) > 5 or len(areas_secundarias) > 5:
                return render_template('crear_cuenta.html', 
                                       error="Solo puedes seleccionar un máximo de 5 áreas secundarias.", 
                                       asignaturas=asignaturas, 
                                       form_data=form_data)

            # Validación de jefe de área
            if es_jefe == 'si':
                if not area_jefe:
                    return render_template('crear_cuenta.html', 
                                           error="Debes seleccionar el área de la que el docente es jefe.", 
                                           asignaturas=asignaturas, 
                                           form_data=form_data)
                areas_permitidas = [str(area_principal)] + [str(a) for a in areas_secundarias]
                if str(area_jefe) not in areas_permitidas:
                    return render_template('crear_cuenta.html', 
                                           error="El docente solo puede ser jefe de su área principal o secundaria.", 
                                           asignaturas=asignaturas, 
                                           form_data=form_data)

        # Seguridad especial para Coordinadores
        if tipo_usuario == 'coordinador':
            es_coord_sesion = session.get('rol') == 'coordinador'
            clave_valida = False

            conn_auth = obtener_conexion()
            if conn_auth and conn_auth.is_connected():
                try:
                    c_auth = conn_auth.cursor(dictionary=True)
                    c_auth.execute("SELECT password FROM usuarios WHERE rol = 'coordinador' AND (estado = 'Activo' OR estado IS NULL);")
                    coords = c_auth.fetchall()
                    c_auth.close()
                    conn_auth.close()
                    for c_row in coords:
                        if verificar_password(c_row['password'], clave_autorizacion):
                            clave_valida = True
                            break
                except Exception:
                    if conn_auth.is_connected():
                        conn_auth.close()

            if not es_coord_sesion and not clave_valida:
                return render_template('crear_cuenta.html', 
                                       error="Para registrar una cuenta de Coordinador se requiere la clave de autorización de Coordinación.", 
                                       asignaturas=asignaturas, 
                                       form_data=form_data)

        # Verificar si usuario ya existe
        conn_check = obtener_conexion()
        if not conn_check or not conn_check.is_connected():
            return render_template('crear_cuenta.html', 
                                   error="Error de conexión con la base de datos.", 
                                   asignaturas=asignaturas, 
                                   form_data=form_data)

        try:
            cur_check = conn_check.cursor(dictionary=True)
            cur_check.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s LIMIT 1;", (usuario,))
            if cur_check.fetchone():
                cur_check.close()
                conn_check.close()
                return render_template('crear_cuenta.html', 
                                       error="Este nombre de usuario ya está registrado.", 
                                       asignaturas=asignaturas, 
                                       form_data=form_data)

            hash_password = generate_password_hash(password)

            if tipo_usuario == 'docente':
                es_coord_autorizo = (session.get('rol') == 'coordinador')
                estado_cuenta = 'Activo' if es_coord_autorizo else 'Inactivo'

                cur_check.execute("SELECT COALESCE(MAX(Doc_CodDocentes), 0) + 1 AS nuevo_id FROM docentes;")
                nuevo_id_docente = cur_check.fetchone()['nuevo_id']

                partes_nombre = nombre_completo.split()
                if len(partes_nombre) >= 2:
                    nombres = " ".join(partes_nombre[:-1])
                    apellidos = partes_nombre[-1]
                else:
                    nombres = nombre_completo
                    apellidos = "-"

                cod_asig_num = int(area_principal) if str(area_principal).isdigit() else 1
                correo_doc = f"{usuario}@asistec.edu"[:30]

                sql_doc = """
                    INSERT INTO docentes (
                        Doc_CodDocentes, Doc_Nombres, Doc_Apellidos, Doc_FechaNacimiento,
                        Doc_Cod_Asignatura, Doc_Telefono, Doc_Correo, Doc_Direcion,
                        Doc_Obcervacion, Doc_Genero
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cur_check.execute(sql_doc, (
                    nuevo_id_docente, nombres, apellidos, '1990-01-01',
                    cod_asig_num, 0, correo_doc, 'Sede Central',
                    'Docente Registrado', 'No especificado'
                ))

                sql_usr = """
                    INSERT INTO usuarios (usuario, password, rol, id_docente, nombre, estado)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cur_check.execute(sql_usr, (
                    usuario, hash_password, 'docente', nuevo_id_docente, nombre_completo, estado_cuenta
                ))

                # Registrar áreas del docente en docente_areas
                # 1. Área principal
                es_jefe_princ = 1 if (es_jefe == 'si' and str(area_jefe) == str(area_principal)) else 0
                cur_check.execute("""
                    INSERT INTO docente_areas (id_docente, id_area, es_principal, es_jefe)
                    VALUES (%s, %s, 1, %s);
                """, (nuevo_id_docente, int(area_principal), es_jefe_princ))

                # 2. Áreas secundarias (entre 0 y 5)
                for a_sec in areas_secundarias:
                    es_jefe_sec = 1 if (es_jefe == 'si' and str(area_jefe) == str(a_sec)) else 0
                    cur_check.execute("""
                        INSERT INTO docente_areas (id_docente, id_area, es_principal, es_jefe)
                        VALUES (%s, %s, 0, %s);
                    """, (nuevo_id_docente, int(a_sec), es_jefe_sec))

                # Registrar en docente_asignaturas para mantener compatibilidad histórica completa
                cur_check.execute("""
                    INSERT INTO docente_asignaturas (id_docente, id_asignatura, es_principal)
                    VALUES (%s, %s, 1);
                """, (nuevo_id_docente, int(area_principal)))

                for a_sec in areas_secundarias:
                    cur_check.execute("""
                        INSERT INTO docente_asignaturas (id_docente, id_asignatura, es_principal)
                        VALUES (%s, %s, 0);
                    """, (nuevo_id_docente, int(a_sec)))

            elif tipo_usuario == 'coordinador':
                # Coordinador
                sql_usr = """
                    INSERT INTO usuarios (usuario, password, rol, id_docente, nombre, estado)
                    VALUES (%s, %s, %s, NULL, %s, %s);
                """
                cur_check.execute(sql_usr, (
                    usuario, hash_password, 'coordinador', nombre_completo, 'Activo'
                ))
            else:
                cur_check.close()
                conn_check.close()
                return render_template('crear_cuenta.html',
                                       error="Tipo de usuario no válido.",
                                       asignaturas=asignaturas,
                                       form_data=form_data), 400

            conn_check.commit()
            cur_check.close()
            conn_check.close()

            if tipo_usuario == 'docente' and not es_coord_autorizo:
                msg_exito = "Cuenta de docente creada con éxito. Por seguridad, se encuentra pendiente de activación por parte de Coordinación antes de poder iniciar sesión."
            else:
                msg_exito = "Cuenta creada exitosamente. Ya puedes iniciar sesión con tu usuario y contraseña."

            return render_template('login.html', exito=msg_exito)

        except Exception as e:
            print(f"[ERROR CREAR CUENTA]: {e}")
            if conn_check and conn_check.is_connected():
                conn_check.close()
            return render_template('crear_cuenta.html', 
                                   error=f"Error al registrar la cuenta: {e}", 
                                   asignaturas=asignaturas, 
                                   form_data=form_data)

    return render_template('crear_cuenta.html', asignaturas=asignaturas)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def obtener_permiso_docentes_tecnologia_bd(conn=None):
    debe_cerrar = False
    if conn is None or not conn.is_connected():
        conn = obtener_conexion()
        debe_cerrar = True
    if not conn or not conn.is_connected():
        return False
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT valor FROM configuracion_sistema WHERE clave = 'permiso_docentes_tecnologia' LIMIT 1;")
        r = cur.fetchone()
        cur.close()
        if debe_cerrar:
            conn.close()
        return bool(r and r['valor'] == '1')
    except Exception:
        if debe_cerrar and conn and conn.is_connected():
            conn.close()
        return False

def obtener_anio_lectivo_activo_bd():
    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return 2026
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT valor FROM configuracion_sistema WHERE clave = 'anio_lectivo_activo' LIMIT 1;")
        r = cur.fetchone()
        cur.close()
        conn.close()
        return int(r['valor']) if r and str(r['valor']).isdigit() else 2026
    except Exception:
        if conn and conn.is_connected():
            conn.close()
        return 2026

def obtener_info_academica_docente(id_docente, conn=None):
    vacio = {
        'area_principal': '',
        'areas_secundarias': [],
        'area_secundaria': 'Ninguna',
        'areas_adicionales': [],
        'asignatura_principal': '',
        'asignaturas_adicionales': [],
        'todas_asignaturas': [],
        'es_jefe': False,
        'areas_jefe': [],
        'area_que_dirige': ''
    }
    if not id_docente:
        return vacio
    debe_cerrar = False
    if conn is None or not conn.is_connected():
        conn = obtener_conexion()
        debe_cerrar = True
    if not conn or not conn.is_connected():
        return vacio
    try:
        cur = conn.cursor(dictionary=True)
        # 1. Obtener áreas del docente
        cur.execute("""
            SELECT da.id_area, da.es_principal, da.es_jefe, a.Asi_NomAsignatura 
            FROM docente_areas da
            JOIN asignatura a ON da.id_area = a.Asi_CodAsignatura
            WHERE da.id_docente = %s
            ORDER BY da.es_principal DESC, da.id ASC;
        """, (id_docente,))
        filas_areas = cur.fetchall()

        area_principal = ''
        areas_secundarias = []
        areas_jefe = []
        for r in filas_areas:
            if r['es_principal']:
                area_principal = r['Asi_NomAsignatura']
            else:
                if r['Asi_NomAsignatura'] not in areas_secundarias:
                    areas_secundarias.append(r['Asi_NomAsignatura'])
            if r['es_jefe']:
                if r['Asi_NomAsignatura'] not in areas_jefe:
                    areas_jefe.append(r['Asi_NomAsignatura'])

        # Fallback a tabla docentes si no hubiera registro en docente_areas
        if not area_principal:
            cur.execute("""
                SELECT a.Asi_NomAsignatura 
                FROM docentes d
                JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
                WHERE d.Doc_CodDocentes = %s LIMIT 1;
            """, (id_docente,))
            f_d = cur.fetchone()
            if f_d:
                area_principal = f_d['Asi_NomAsignatura']

        # Lista de todas las asignaturas asignadas al docente
        todas_asignaturas = []
        if area_principal and area_principal not in todas_asignaturas:
            todas_asignaturas.append(area_principal)
        for a in areas_secundarias:
            if a not in todas_asignaturas:
                todas_asignaturas.append(a)

        area_sec_str = ", ".join(areas_secundarias) if areas_secundarias else 'Ninguna'

        cur.close()
        if debe_cerrar:
            conn.close()

        return {
            'area_principal': area_principal,
            'areas_secundarias': areas_secundarias,
            'area_secundaria': area_sec_str,
            'areas_adicionales': areas_secundarias,
            'asignatura_principal': area_principal,
            'asignaturas_adicionales': areas_secundarias,
            'todas_asignaturas': todas_asignaturas,
            'es_jefe': len(areas_jefe) > 0,
            'areas_jefe': areas_jefe,
            'area_que_dirige': areas_jefe[0] if areas_jefe else ''
        }
    except Exception as e:
        print(f"[ERROR INFO ACADEMICA DOCENTE]: {e}")
        if debe_cerrar and conn and conn.is_connected():
            conn.close()
        return vacio

def docente_tiene_permiso_materia(id_docente, materia):
    """
    Verifica de forma estricta si un docente tiene asignada una materia académica
    (como área principal o secundaria) en la base de datos institucional.
    """
    if not id_docente or not materia:
        return False
    doc_info = obtener_info_academica_docente(id_docente)
    todas = doc_info.get('todas_asignaturas', [])
    m_norm = normalizar_nombre_asignatura(materia)
    for t in todas:
        if normalizar_nombre_asignatura(t) == m_norm:
            return True
    return False

def obtener_area_docente(id_docente):
    if not id_docente:
        return ""
    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return ""
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.Asi_NomAsignatura 
            FROM docentes d
            JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            WHERE d.Doc_CodDocentes = %s LIMIT 1;
        """, (id_docente,))
        r = cur.fetchone()
        cur.close()
        conn.close()
        return r['Asi_NomAsignatura'] if r else ""
    except Exception:
        if conn and conn.is_connected():
            conn.close()
        return ""


def obtener_areas_disponibles_bd(conn=None):
    debe_cerrar = False
    if conn is None or not conn.is_connected():
        conn = obtener_conexion()
        debe_cerrar = True
    if not conn or not conn.is_connected():
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT DISTINCT Asi_NomAsignatura FROM asignatura ORDER BY Asi_NomAsignatura;")
        rows = cur.fetchall()
        cur.close()
        if debe_cerrar:
            conn.close()
        return [r['Asi_NomAsignatura'] for r in rows if r.get('Asi_NomAsignatura')]
    except Exception as e:
        print(f"[ERROR OBTENER AREAS BD]: {e}")
        if debe_cerrar and conn and conn.is_connected():
            conn.close()
        return []

def obtener_docentes_con_permisos(conn=None):
    debe_cerrar = False
    if conn is None or not conn.is_connected():
        conn = obtener_conexion()
        debe_cerrar = True
    if not conn or not conn.is_connected():
        return []
    try:
        cur = conn.cursor(dictionary=True)
        # 1. Consulta optimizada de usuarios y docentes con fallback a su asignatura principal inicial
        cur.execute("""
            SELECT u.id_usuario, u.usuario, u.id_docente, u.nombre, COALESCE(u.permiso_matricula, 0) AS permiso_matricula,
                   d.Doc_Nombres, d.Doc_Apellidos,
                   fb_a.Asi_NomAsignatura AS fallback_area
            FROM usuarios u
            LEFT JOIN docentes d ON u.id_docente = d.Doc_CodDocentes
            LEFT JOIN asignatura fb_a ON d.Doc_Cod_Asignatura = fb_a.Asi_CodAsignatura
            WHERE u.rol = 'docente'
            ORDER BY COALESCE(NULLIF(u.nombre, ''), CONCAT(COALESCE(d.Doc_Nombres, ''), ' ', COALESCE(d.Doc_Apellidos, '')), u.usuario) ASC, u.id_usuario ASC;
        """)
        filas = cur.fetchall()

        # 2. Obtener todas las áreas asignadas en docente_areas mediante consulta agrupada (1 solo viaje a la BD)
        ids_docentes = [f['id_docente'] for f in filas if f.get('id_docente')]
        areas_por_docente = {}
        if ids_docentes:
            format_strings = ','.join(['%s'] * len(ids_docentes))
            cur.execute(f"""
                SELECT da.id_docente, da.es_principal, da.es_jefe, a.Asi_NomAsignatura
                FROM docente_areas da
                JOIN asignatura a ON da.id_area = a.Asi_CodAsignatura
                WHERE da.id_docente IN ({format_strings})
                ORDER BY da.es_principal DESC, da.id ASC;
            """, tuple(ids_docentes))
            filas_areas = cur.fetchall()

            for r in filas_areas:
                idd = r['id_docente']
                if idd not in areas_por_docente:
                    areas_por_docente[idd] = {'principal': '', 'secundarias': [], 'jefe': []}
                if r['es_principal']:
                    if not areas_por_docente[idd]['principal']:
                        areas_por_docente[idd]['principal'] = r['Asi_NomAsignatura']
                else:
                    if r['Asi_NomAsignatura'] not in areas_por_docente[idd]['secundarias']:
                        areas_por_docente[idd]['secundarias'].append(r['Asi_NomAsignatura'])
                if r['es_jefe']:
                    if r['Asi_NomAsignatura'] not in areas_por_docente[idd]['jefe']:
                        areas_por_docente[idd]['jefe'].append(r['Asi_NomAsignatura'])

        cur.close()
        if debe_cerrar:
            conn.close()

        resultado = []
        for f in filas:
            idd = f.get('id_docente')
            info_areas = areas_por_docente.get(idd, {'principal': '', 'secundarias': [], 'jefe': []})

            area_principal = info_areas['principal']
            # Fallback a tabla docentes si no hubiera registro en docente_areas
            if not area_principal and f.get('fallback_area'):
                area_principal = f['fallback_area']

            areas_sec = info_areas['secundarias']
            area_sec_str = ", ".join(areas_sec) if areas_sec else 'Ninguna'

            nombre_doc = (f.get('nombre') or '').strip()
            if not nombre_doc:
                nom = (f.get('Doc_Nombres') or '').strip()
                ape = (f.get('Doc_Apellidos') or '').strip()
                nombre_doc = f"{nom} {ape}".strip() or f.get('usuario')

            resultado.append({
                'id_usuario': f['id_usuario'],
                'usuario': f['usuario'],
                'nombre': nombre_doc,
                'id_docente': f['id_docente'],
                'area_principal': area_principal or 'Sin asignar',
                'areas_secundarias': area_sec_str,
                'permiso_matricula': 1 if f.get('permiso_matricula') == 1 else 0
            })
        return resultado
    except Exception as e:
        print(f"[ERROR OBTENER DOCENTES PERMISOS]: {e}")
        if debe_cerrar and conn and conn.is_connected():
            conn.close()
        return []

def tiene_permiso_gestion_estudiantes():
    if 'usuario' not in session:
        return False
    rol = session.get('rol')
    if rol == 'coordinador':
        return True
    if rol == 'docente':
        # 1. Permiso individual concedido en la tabla usuarios
        id_usuario = session.get('id_usuario')
        usuario = session.get('usuario')
        conn = obtener_conexion()
        if conn and conn.is_connected():
            try:
                cur = conn.cursor(dictionary=True)
                if id_usuario:
                    cur.execute("SELECT COALESCE(permiso_matricula, 0) AS permiso_matricula FROM usuarios WHERE id_usuario = %s LIMIT 1;", (id_usuario,))
                else:
                    cur.execute("SELECT COALESCE(permiso_matricula, 0) AS permiso_matricula FROM usuarios WHERE usuario = %s LIMIT 1;", (usuario,))
                r = cur.fetchone()
                cur.close()
                conn.close()
                if r and r.get('permiso_matricula') == 1:
                    return True
            except Exception as e:
                print(f"[ERROR VERIFICAR PERMISO MATRICULA]: {e}")
                if conn and conn.is_connected():
                    conn.close()

        # 2. Permiso institucional para docentes de tecnología e informática
        id_docente = session.get('id_docente')
        area = normalizar_nombre_asignatura(obtener_area_docente(id_docente))
        if area == 'tecnologia_e_informatica':
            return obtener_permiso_docentes_tecnologia_bd()
    return False

@app.route('/docente')
@app.route('/panel_docente')
def docente():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if session.get('rol') != 'docente':
        if session.get('rol') == 'rectoria':
            return redirect(url_for('rectoria'))
        return redirect(url_for('coordinador'))
    puede_gestionar = tiene_permiso_gestion_estudiantes()
    docente_info = obtener_info_academica_docente(session.get('id_docente'))
    error_msg = request.args.get('error')
    mensaje_msg = request.args.get('mensaje')
    return render_template('docente.html',
                           usuario=session.get('usuario'),
                           rol='docente',
                           puede_gestionar_estudiantes=puede_gestionar,
                           docente_info=docente_info,
                           error=error_msg,
                           mensaje=mensaje_msg)

@app.route('/coordinador')
def coordinador():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if session.get('rol') != 'coordinador':
        if session.get('rol') == 'rectoria':
            return redirect(url_for('rectoria'))
        return redirect(url_for('docente'))

    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return render_template(
            'coordinador.html',
            usuario=session.get('usuario'),
            rol='coordinador',
            puede_gestionar_estudiantes=True,
            permiso_docentes_tec=False,
            docentes_registrados=[],
            total_docentes=0,
            total_autorizados=0,
            total_sin_permiso=0,
            todas_areas=[]
        )

    try:
        permiso_tec = obtener_permiso_docentes_tecnologia_bd(conn=conn)
        docentes_registrados = obtener_docentes_con_permisos(conn=conn)
        todas_areas = obtener_areas_disponibles_bd(conn=conn)
    finally:
        if conn and conn.is_connected():
            conn.close()

    total_docentes = len(docentes_registrados)
    total_autorizados = sum(1 for d in docentes_registrados if d.get('permiso_matricula') == 1)
    total_sin_permiso = total_docentes - total_autorizados

    return render_template(
        'coordinador.html',
        usuario=session.get('usuario'),
        rol='coordinador',
        puede_gestionar_estudiantes=True,
        permiso_docentes_tec=permiso_tec,
        docentes_registrados=docentes_registrados,
        total_docentes=total_docentes,
        total_autorizados=total_autorizados,
        total_sin_permiso=total_sin_permiso,
        todas_areas=todas_areas
    )


@app.route('/coordinador/cambiar_permiso_docente', methods=['POST'])
def cambiar_permiso_docente():
    if 'usuario' not in session or session.get('rol') != 'coordinador':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        return redirect(url_for('login'))

    data = request.get_json(silent=True) or request.form
    id_usuario = data.get('id_usuario')
    nuevo_permiso = data.get('permiso')

    if not id_usuario:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'error': 'ID de docente no proporcionado'}), 400
        return redirect(url_for('coordinador'))

    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'error': 'Error de conexión con la base de datos'}), 500
        return redirect(url_for('coordinador'))

    try:
        cur = conn.cursor(dictionary=True)
        if nuevo_permiso is None or nuevo_permiso == '':
            cur.execute("SELECT COALESCE(permiso_matricula, 0) AS permiso_matricula FROM usuarios WHERE id_usuario = %s AND rol = 'docente' LIMIT 1;", (id_usuario,))
            r = cur.fetchone()
            if not r:
                cur.close()
                conn.close()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                    return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
                return redirect(url_for('coordinador'))
            val_actual = r['permiso_matricula']
            nuevo_val = 0 if val_actual == 1 else 1
        else:
            nuevo_val = 1 if str(nuevo_permiso).strip().lower() in ('1', 'true', 'autorizado', 'si') else 0

        cur.execute("UPDATE usuarios SET permiso_matricula = %s WHERE id_usuario = %s AND rol = 'docente';", (nuevo_val, id_usuario))
        conn.commit()

        cur.execute("SELECT COUNT(*) AS total FROM usuarios WHERE rol = 'docente';")
        total_docentes = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS autorizados FROM usuarios WHERE rol = 'docente' AND permiso_matricula = 1;")
        total_autorizados = cur.fetchone()['autorizados']
        total_sin_permiso = total_docentes - total_autorizados

        cur.close()
        conn.close()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({
                'success': True,
                'mensaje': 'Permiso actualizado con éxito',
                'id_usuario': int(id_usuario),
                'nuevo_permiso': nuevo_val,
                'total_docentes': total_docentes,
                'total_autorizados': total_autorizados,
                'total_sin_permiso': total_sin_permiso
            })
        return redirect(url_for('coordinador'))
    except Exception as e:
        print(f"[ERROR CAMBIAR PERMISO DOCENTE]: {e}")
        if conn and conn.is_connected():
            conn.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        return redirect(url_for('coordinador'))

@app.route('/rectoria')
@app.route('/panel_rectoria')
def rectoria():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if session.get('rol') != 'rectoria':
        if session.get('rol') == 'docente':
            return redirect(url_for('docente'))
        elif session.get('rol') == 'coordinador':
            return redirect(url_for('coordinador'))
        return redirect(url_for('login'))
    return render_template('rectoria.html', usuario=session.get('usuario'), nombre=session.get('nombre', 'Rector Académico'), rol='rectoria', puede_gestionar_estudiantes=False)

@app.route('/toggle_permiso_docentes_tec', methods=['POST'])
def toggle_permiso_docentes_tec():
    if 'usuario' not in session or session.get('rol') != 'coordinador':
        return redirect(url_for('login'))
    
    conn = obtener_conexion()
    if conn and conn.is_connected():
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT valor FROM configuracion_sistema WHERE clave = 'permiso_docentes_tecnologia' LIMIT 1;")
            r = cur.fetchone()
            val_actual = r['valor'] if r else '0'
            param_permiso = request.form.get('permiso')
            if param_permiso in ('0', '1'):
                nuevo_val = param_permiso
            else:
                nuevo_val = '0' if val_actual == '1' else '1'
            cur.execute("""
                INSERT INTO configuracion_sistema (clave, valor) 
                VALUES ('permiso_docentes_tecnologia', %s)
                ON DUPLICATE KEY UPDATE valor = %s;
            """, (nuevo_val, nuevo_val))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[ERROR TOGGLE PERMISO]: {e}")
            if conn and conn.is_connected():
                conn.close()
    return redirect(url_for('coordinador'))

# =========================================================================
# 2. 📝 REGISTRO DE INASISTENCIA (NUEVO MÓDULO OPERATIVO MATRIZ)
# =========================================================================

@app.route('/registro_inasistencia', methods=['GET'])
def registro_inasistencia():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')

    grado_sel = request.args.get('grado', '').strip()
    grupo_sel = request.args.get('grupo', '').strip()
    jornada_sel = request.args.get('jornada', '').strip()
    asignatura_sel = request.args.get('asignatura', '').strip()
    sede_sel = request.args.get('sede', '').strip()
    modalidad_sel = request.args.get('modalidad', 'General').strip()
    fecha_sel = request.args.get('fecha', '').strip()
    estudiante_sel = request.args.get('estudiante', '').strip()
    if not fecha_sel:
        fecha_sel = datetime.now().strftime("%Y-%m-%d")
    if grupo_sel and not str(grupo_sel).isdigit():
        _c_norm = obtener_conexion()
        if _c_norm and _c_norm.is_connected():
            _cur_n = _c_norm.cursor(dictionary=True)
            _cur_n.execute("SELECT Gru_Codigo FROM grupo WHERE Gru_NombreGrupo = %s LIMIT 1;", (grupo_sel,))
            _rg = _cur_n.fetchone()
            _cur_n.close()
            _c_norm.close()
            if _rg:
                grupo_sel = str(_rg['Gru_Codigo'])

    mensaje = request.args.get('mensaje', '').strip()
    error = request.args.get('error', '').strip()
    aviso = request.args.get('aviso', '').strip()

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('registro_inasistencia.html', error="No hay conexión con la base de datos MySQL.", usuario=usuario, rol=rol)

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        grupos = []
        if grado_sel:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_sel,))
            grupos = cursor.fetchall()
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
            grupos = cursor.fetchall()

        asignaturas_disponibles = obtener_asignaturas_validas(grado_sel, modalidad_sel)
        if session.get('rol') == 'docente':
            doc_info = obtener_info_academica_docente(session.get('id_docente'))
            if doc_info.get('todas_asignaturas'):
                materias_doc = [m for m in asignaturas_disponibles if m in doc_info['todas_asignaturas']]
                asignaturas_disponibles = materias_doc if materias_doc else doc_info['todas_asignaturas']

        lista_estudiantes_filtro = obtener_estudiantes_por_grado_grupo(grado_sel, grupo_sel, jornada_sel, sede_sel)

        grupo_nombre_sel = ''
        if grupo_sel:
            for gr in grupos:
                if str(gr['Gru_Codigo']) == str(grupo_sel):
                    grupo_nombre_sel = gr['Gru_NombreGrupo']
                    break

        estudiantes = None
        if request.args.get('cargar'):
            faltantes = []
            if not grado_sel: faltantes.append("Grado")
            if not grupo_sel: faltantes.append("Grupo")
            if not jornada_sel: faltantes.append("Jornada")
            if not asignatura_sel: faltantes.append("Asignatura")
            if not sede_sel: faltantes.append("Sede")
            if not fecha_sel: faltantes.append("Fecha")

            if grado_sel and asignatura_sel and not asignatura_valida(grado_sel, modalidad_sel, asignatura_sel):
                error = f"Aviso Académico: La asignatura '{asignatura_sel}' no corresponde al Grado {grado_sel} (Modalidad: {modalidad_sel})."
            elif session.get('rol') == 'docente' and asignatura_sel and not docente_tiene_permiso_materia(session.get('id_docente'), asignatura_sel):
                error = f"Acceso denegado: No tienes asignada la asignatura '{asignatura_sel}'."
            elif faltantes:
                error = f"Por favor completa todos los campos obligatorios antes de cargar estudiantes. Falta: {', '.join(faltantes)}."
            else:
                sql_est = """
                    SELECT e.Est_CodEstudiante, e.Est_Nombre, e.Est_Apellido, e.Est_Cod_Grado, e.Est_Cod_Grupo, e.Est_Cod_SedeEstudiantil, e.Est_Jornada, s.Sed_NomSede
                    FROM estudiantes e
                    LEFT JOIN sedes s ON e.Est_Cod_SedeEstudiantil = s.Sed_CodigoSede
                    WHERE e.Est_Cod_Grado = %s AND e.Est_Cod_Grupo = %s
                """
                p_sql = [grado_sel, grupo_sel]
                if jornada_sel:
                    if 'ma' in jornada_sel.lower() and 'ana' in jornada_sel.lower():
                        sql_est += " AND (e.Est_Jornada LIKE %s OR e.Est_Jornada LIKE %s)"
                        p_sql.extend(['Mañana%', 'Ma%ana%'])
                    else:
                        sql_est += " AND e.Est_Jornada LIKE %s"
                        p_sql.append(f"{jornada_sel}%")
                if sede_sel:
                    if str(sede_sel).isdigit():
                        sql_est += " AND e.Est_Cod_SedeEstudiantil = %s"
                        p_sql.append(int(sede_sel))
                    else:
                        sql_est += " AND (s.Sed_NomSede LIKE %s OR %s LIKE CONCAT('%%', s.Sed_NomSede, '%%'))"
                        p_sql.extend([f"%{sede_sel}%", sede_sel])

                if estudiante_sel and estudiante_sel != 'todos':
                    sql_est += " AND e.Est_CodEstudiante = %s"
                    p_sql.append(estudiante_sel)

                sql_est += " ORDER BY e.Est_Apellido ASC, e.Est_Nombre ASC;"
                cursor.execute(sql_est, tuple(p_sql))
                filas_est = cursor.fetchall()

                asig_nom_real = asignatura_sel
                if str(asignatura_sel).isdigit():
                    cursor.execute("SELECT Asi_NomAsignatura FROM asignatura WHERE Asi_CodAsignatura = %s;", (int(asignatura_sel),))
                    res_as = cursor.fetchone()
                    if res_as:
                        asig_nom_real = res_as['Asi_NomAsignatura']

                estudiantes = []
                for est in filas_est:
                    sql_asist = """
                        SELECT Reg_CodRegistroAsistencia, Reg_Observacion, Reg_FechaHoraIngreso
                        FROM registroasistencia
                        WHERE Reg_CodEstudiante = %s
                          AND Reg_FechaHoraIngreso LIKE %s
                          AND (Reg_Asignatura = %s OR Reg_Asignatura LIKE %s OR %s LIKE CONCAT('%%', Reg_Asignatura, '%%'))
                        ORDER BY Reg_CodRegistroAsistencia DESC LIMIT 1;
                    """
                    cursor.execute(sql_asist, (est['Est_CodEstudiante'], f"{fecha_sel}%", asig_nom_real, f"%{asig_nom_real}%", asig_nom_real))
                    reg_exist = cursor.fetchone()

                    tiene_inasistencia = False
                    estado_actual = None
                    obs_existente = ''

                    if reg_exist:
                        raw_obs = reg_exist['Reg_Observacion'] or ''
                        if ':' in raw_obs:
                            st, det = raw_obs.split(':', 1)
                            estado_actual = st.strip()
                            obs_existente = det.strip()
                        else:
                            estado_actual = raw_obs.strip()
                        if 'ausente' in estado_actual.lower() or 'inasistencia' in estado_actual.lower():
                            tiene_inasistencia = True

                    est_dict = dict(est)
                    est_dict['tiene_inasistencia'] = tiene_inasistencia
                    est_dict['estado_actual'] = estado_actual
                    est_dict['obs_existente'] = obs_existente
                    estudiantes.append(est_dict)

        cursor.close()
        conexion.close()

        return render_template(
            'registro_inasistencia.html',
            grados=grados,
            grupos=grupos,
            asignaturas=asignaturas_disponibles,
            modalidades=MODALIDADES_TECNICAS,
            jornadas=JORNADAS_DISPONIBLES,
            sedes=SEDES_DISPONIBLES,
            grado_seleccionado=grado_sel,
            grupo_seleccionado=grupo_sel,
            grupo_nombre_sel=grupo_nombre_sel,
            jornada_seleccionada=jornada_sel,
            asignatura_seleccionada=asignatura_sel,
            sede_seleccionada=sede_sel,
            modalidad_seleccionada=modalidad_sel,
            fecha_seleccionada=fecha_sel,
            lista_estudiantes_filtro=lista_estudiantes_filtro,
            estudiante_seleccionado=estudiante_sel,
            estudiantes=estudiantes,
            error=error,
            mensaje=mensaje,
            aviso=aviso,
            usuario=usuario,
            rol=rol
        )
    except Exception as e:
        print(f"[ERROR REGISTRO INASISTENCIA]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('registro_inasistencia.html', error=f"Error cargando módulo: {e}", usuario=usuario, rol=rol)

@app.route('/guardar_inasistencia', methods=['POST'])
def guardar_inasistencia():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')

    if rol == 'rectoria':
        return redirect(url_for('registro_inasistencia', error="Acceso denegado: El rol de Rectoría es exclusivamente de consulta y no puede registrar inasistencias."))

    id_docente = session.get('id_docente')
    if not id_docente and rol == 'coordinador':
        id_docente = 1

    if not id_docente:
        return redirect(url_for('registro_inasistencia', error="Error de seguridad: No hay docente en la sesión."))

    grado_id = request.form.get('grado_id', '').strip()
    grupo_id = request.form.get('grupo_id', '').strip()
    jornada_id = request.form.get('jornada_id', '').strip()
    asignatura_nombre = request.form.get('asignatura_nombre', '').strip()
    sede_nombre = request.form.get('sede_nombre', '').strip()
    modalidad_id = request.form.get('modalidad_id', 'General').strip()
    fecha_registro = request.form.get('fecha_registro', '').strip()
    if not fecha_registro:
        fecha_registro = datetime.now().strftime("%Y-%m-%d")

    inasistentes_raw = [str(e).strip() for e in request.form.getlist('inasistentes') if str(e).strip()]
    tardes_raw = [str(e).strip() for e in request.form.getlist('llegadas_tarde') if str(e).strip()]

    # 1. Validación de selección: Debe permitirse solo ausentes, solo tarde o ambos (personas distintas).
    # Debe rechazarse cuando ambas listas estén vacías.
    if not inasistentes_raw and not tardes_raw:
        return redirect(url_for('registro_inasistencia',
            cargar=1,
            grado=grado_id,
            grupo=grupo_id,
            jornada=jornada_id,
            asignatura=asignatura_nombre,
            sede=sede_nombre,
            modalidad=modalidad_id,
            fecha=fecha_registro,
            error="Debe seleccionar al menos un estudiante inasistente."
        ))

    # 2. Validación de identificadores numéricos ASCII en ambas listas
    for est_raw in inasistentes_raw + tardes_raw:
        if not re.fullmatch(r"[0-9]+", est_raw):
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                error="Identificador de estudiante inválido (debe ser numérico)."
            ))

    # 3. Validar identificadores duplicados dentro de cada lista
    if len(inasistentes_raw) != len(set(inasistentes_raw)) or len(tardes_raw) != len(set(tardes_raw)):
        return redirect(url_for('registro_inasistencia',
            cargar=1,
            grado=grado_id,
            grupo=grupo_id,
            jornada=jornada_id,
            asignatura=asignatura_nombre,
            sede=sede_nombre,
            modalidad=modalidad_id,
            fecha=fecha_registro,
            error="Solicitud inválida: Se detectaron identificadores duplicados en el envío."
        ))

    # 4. Validar colisiones entre ausentes y llegadas tarde
    colisiones = set(inasistentes_raw).intersection(set(tardes_raw))
    if colisiones:
        return redirect(url_for('registro_inasistencia',
            cargar=1,
            grado=grado_id,
            grupo=grupo_id,
            jornada=jornada_id,
            asignatura=asignatura_nombre,
            sede=sede_nombre,
            modalidad=modalidad_id,
            fecha=fecha_registro,
            error="Solicitud inválida: Un estudiante no puede ser registrado como ausente y llegada tarde simultáneamente."
        ))

    # Mapeo de estado por estudiante ('Ausente' o 'Tarde')
    estado_por_estudiante = {}
    for e in inasistentes_raw:
        estado_por_estudiante[e] = 'Ausente'
    for e in tardes_raw:
        estado_por_estudiante[e] = 'Tarde'

    inasistentes = list(estado_por_estudiante.keys())

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return redirect(url_for('registro_inasistencia',
            cargar=1,
            grado=grado_id,
            grupo=grupo_id,
            jornada=jornada_id,
            asignatura=asignatura_nombre,
            sede=sede_nombre,
            modalidad=modalidad_id,
            fecha=fecha_registro,
            error="No se pudo conectar a MySQL."
        ))

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT Gra_NombreGrado FROM grado WHERE Gra_Codigo = %s;", (grado_id,))
        res_g = cursor.fetchone()
        if not res_g:
            cursor.close()
            conexion.close()
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                error="El grado seleccionado no existe."
            ))
        grado_nom = res_g['Gra_NombreGrado']

        # 1. VALIDACIÓN DEL GRUPO
        cursor.execute("SELECT Gru_NombreGrupo, Gru_Cod_Grado FROM grupo WHERE Gru_Codigo = %s;", (grupo_id,))
        res_grp = cursor.fetchone()
        if not res_grp:
            cursor.close()
            conexion.close()
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                error="El grupo seleccionado no existe."
            ))
        if str(res_grp.get('Gru_Cod_Grado')) != str(grado_id):
            cursor.close()
            conexion.close()
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                error=f"Rechazado por regla académica: El grupo '{res_grp.get('Gru_NombreGrupo')}' no corresponde al Grado {grado_nom}."
            ))

        asig_nom_real = asignatura_nombre
        if str(asignatura_nombre).isdigit():
            cursor.execute("SELECT Asi_NomAsignatura FROM asignatura WHERE Asi_CodAsignatura = %s;", (int(asignatura_nombre),))
            res_as = cursor.fetchone()
            if res_as:
                asig_nom_real = res_as['Asi_NomAsignatura']

        # Validación académica estricta
        if not asignatura_valida(grado_nom, modalidad_id, asig_nom_real):
            cursor.close()
            conexion.close()
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                error=f"Rechazado por regla académica: La asignatura '{asig_nom_real}' no está permitida para Grado {grado_nom} (Modalidad: {modalidad_id})."
            ))

        # Validación estricta de asignación de materia al docente
        if rol == 'docente':
            if not docente_tiene_permiso_materia(id_docente, asig_nom_real):
                cursor.close()
                conexion.close()
                return redirect(url_for('registro_inasistencia',
                    cargar=1,
                    grado=grado_id,
                    grupo=grupo_id,
                    jornada=jornada_id,
                    asignatura=asignatura_nombre,
                    sede=sede_nombre,
                    modalidad=modalidad_id,
                    fecha=fecha_registro,
                    error=f"Acceso denegado: No tienes asignada la asignatura '{asig_nom_real}'."
                ))

        # 2. VALIDACIÓN DE ESTUDIANTES
        estudiantes_unicos = [int(e) for e in inasistentes]

        # 1.1 RESOLUCIÓN Y VALIDACIÓN DE SEDE MEDIANTE CONSULTA PARAMETRIZADA
        cursor.execute("SELECT Sed_CodigoSede FROM sedes WHERE Sed_NomSede = %s LIMIT 1;", (sede_nombre,))
        res_sed = cursor.fetchone()
        if not res_sed and str(sede_nombre).isdigit():
            cursor.execute("SELECT Sed_CodigoSede FROM sedes WHERE Sed_CodigoSede = %s LIMIT 1;", (int(sede_nombre),))
            res_sed = cursor.fetchone()
        if not res_sed:
            cursor.close()
            conexion.close()
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                error=f"La sede '{sede_nombre}' no existe en el sistema."
            ))
        sede_cod_esperado = res_sed['Sed_CodigoSede']

        # Normalización controlada de jornada para igualdad exacta
        def normalizar_jornada(j):
            val = str(j or '').strip().lower()
            val = val.replace('ñ', 'n').replace('ã±', 'n').replace('\ufffd', 'n')
            return val

        # Consultar y verificar cada estudiante en la base de datos
        estudiantes_validados = []
        nombres_estudiantes_validados = {}

        sql_verificar_est = """
            SELECT e.Est_CodEstudiante, e.Est_Nombre, e.Est_Apellido, e.Est_Cod_Grado,
                   e.Est_Cod_Grupo, e.Est_Jornada, e.Est_Estado, e.Est_Cod_SedeEstudiantil, s.Sed_NomSede
            FROM estudiantes e
            LEFT JOIN sedes s ON e.Est_Cod_SedeEstudiantil = s.Sed_CodigoSede
            WHERE e.Est_CodEstudiante = %s;
        """

        for est_id in estudiantes_unicos:
            cursor.execute(sql_verificar_est, (est_id,))
            est_info = cursor.fetchone()

            # Verificar existencia del estudiante
            if not est_info:
                cursor.close()
                conexion.close()
                return redirect(url_for('registro_inasistencia',
                    cargar=1,
                    grado=grado_id,
                    grupo=grupo_id,
                    jornada=jornada_id,
                    asignatura=asignatura_nombre,
                    sede=sede_nombre,
                    modalidad=modalidad_id,
                    fecha=fecha_registro,
                    error=f"El estudiante con código {est_id} no existe en el sistema."
                ))

            nom_completo = f"{est_info['Est_Apellido']} {est_info['Est_Nombre']}".strip()

            # Verificar estado Activo
            if str(est_info.get('Est_Estado', '')).strip().lower() != 'activo':
                cursor.close()
                conexion.close()
                return redirect(url_for('registro_inasistencia',
                    cargar=1,
                    grado=grado_id,
                    grupo=grupo_id,
                    jornada=jornada_id,
                    asignatura=asignatura_nombre,
                    sede=sede_nombre,
                    modalidad=modalidad_id,
                    fecha=fecha_registro,
                    error=f"El estudiante {nom_completo} (ID: {est_id}) no se encuentra activo."
                ))

            # Verificar pertenencia al grado y grupo seleccionados
            if str(est_info.get('Est_Cod_Grado')) != str(grado_id) or str(est_info.get('Est_Cod_Grupo')) != str(grupo_id):
                cursor.close()
                conexion.close()
                return redirect(url_for('registro_inasistencia',
                    cargar=1,
                    grado=grado_id,
                    grupo=grupo_id,
                    jornada=jornada_id,
                    asignatura=asignatura_nombre,
                    sede=sede_nombre,
                    modalidad=modalidad_id,
                    fecha=fecha_registro,
                    error=f"El estudiante {nom_completo} (ID: {est_id}) no pertenece al Grado y Grupo seleccionados."
                ))

            # 1. VERIFICAR JORNADA MEDIANTE NORMALIZACIÓN CONTROLADA E IGUALDAD EXACTA
            if jornada_id:
                if normalizar_jornada(est_info.get('Est_Jornada')) != normalizar_jornada(jornada_id):
                    cursor.close()
                    conexion.close()
                    return redirect(url_for('registro_inasistencia',
                        cargar=1,
                        grado=grado_id,
                        grupo=grupo_id,
                        jornada=jornada_id,
                        asignatura=asignatura_nombre,
                        sede=sede_nombre,
                        modalidad=modalidad_id,
                        fecha=fecha_registro,
                        error=f"El estudiante {nom_completo} (ID: {est_id}) no corresponde a la jornada {jornada_id}."
                    ))

            # 2. VERIFICAR SEDE MEDIANTE COMPARACIÓN EXACTA CON Est_Cod_SedeEstudiantil
            if str(est_info.get('Est_Cod_SedeEstudiantil')) != str(sede_cod_esperado):
                cursor.close()
                conexion.close()
                return redirect(url_for('registro_inasistencia',
                    cargar=1,
                    grado=grado_id,
                    grupo=grupo_id,
                    jornada=jornada_id,
                    asignatura=asignatura_nombre,
                    sede=sede_nombre,
                    modalidad=modalidad_id,
                    fecha=fecha_registro,
                    error=f"El estudiante {nom_completo} (ID: {est_id}) no pertenece a la sede {sede_nombre}."
                ))

            estudiantes_validados.append(est_id)
            nombres_estudiantes_validados[est_id] = nom_completo

        ahora = datetime.now()
        hora_actual = ahora.strftime("%H:%M:%S")
        fecha_hora_guardar = f"{fecha_registro} {hora_actual}"

        sql_check = """
            SELECT Reg_CodRegistroAsistencia, Reg_Observacion 
            FROM registroasistencia 
            WHERE Reg_CodEstudiante = %s 
              AND Reg_FechaHoraIngreso LIKE %s 
              AND (Reg_Asignatura = %s OR Reg_Asignatura LIKE %s OR %s LIKE CONCAT('%%', Reg_Asignatura, '%%'))
              AND (Reg_Observacion LIKE 'Ausente%%' OR Reg_Observacion LIKE 'Inasistencia%%' OR Reg_Observacion LIKE 'Tarde%%');
        """

        sql_insert = """
            INSERT INTO registroasistencia (Reg_CodEstudiante, Reg_CodDocente, Reg_FechaHoraIngreso, Reg_Observacion, Reg_Jornada, Reg_Sede, Reg_Asignatura)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

        guardados = 0
        ya_existentes = 0
        nombres_existentes = []

        # 3. CICLO DE INSERCIÓN: Utiliza EXCLUSIVAMENTE los identificadores previamente validados
        for est_id in estudiantes_validados:
            cursor.execute(sql_check, (est_id, f"{fecha_registro}%", asig_nom_real, f"%{asig_nom_real}%", asig_nom_real))
            duplicado = cursor.fetchone()

            nom_est_str = nombres_estudiantes_validados.get(est_id, f"Código {est_id}")

            if duplicado:
                ya_existentes += 1
                nombres_existentes.append(nom_est_str)
            else:
                tipo_est = estado_por_estudiante.get(str(est_id), 'Ausente')
                obs = request.form.get(f'obs_{est_id}', '').strip()
                obs_final = f"{tipo_est}: {obs}" if obs else tipo_est
                if len(obs_final) > 100:
                    obs_final = obs_final[:100]
                cursor.execute(sql_insert, (est_id, id_docente, fecha_hora_guardar, obs_final, jornada_id, sede_nombre, asig_nom_real))
                guardados += 1

        conexion.commit()
        cursor.close()
        conexion.close()

        # Determinar avisos y mensajes según requerimiento
        if guardados == 0 and ya_existentes > 0:
            msg_aviso = "El estudiante ya tiene una inasistencia registrada para esta fecha y asignatura." if ya_existentes == 1 else "Los estudiantes ya tienen una inasistencia registrada para esta fecha y asignatura."
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                aviso=msg_aviso
            ))
        elif guardados > 0 and ya_existentes == 0:
            msg_ok = "Inasistencia registrada correctamente." if guardados == 1 else "Inasistencias registradas correctamente."
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                mensaje=msg_ok
            ))
        else:
            msg_ok = f"Inasistencia registrada correctamente ({guardados} guardada(s))."
            msg_aviso = f"Aviso: {', '.join(nombres_existentes)} ya tenía(n) inasistencia registrada para esta fecha y asignatura."
            return redirect(url_for('registro_inasistencia',
                cargar=1,
                grado=grado_id,
                grupo=grupo_id,
                jornada=jornada_id,
                asignatura=asignatura_nombre,
                sede=sede_nombre,
                modalidad=modalidad_id,
                fecha=fecha_registro,
                mensaje=msg_ok,
                aviso=msg_aviso
            ))

    except Exception as e:
        print(f"[ERROR GUARDAR INASISTENCIA]: {e}")
        if conexion and conexion.is_connected():
            try:
                conexion.rollback()
            except Exception:
                pass
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
            conexion.close()
        return redirect(url_for('registro_inasistencia',
            cargar=1,
            grado=grado_id,
            grupo=grupo_id,
            jornada=jornada_id,
            asignatura=asignatura_nombre,
            sede=sede_nombre,
            modalidad=modalidad_id,
            fecha=fecha_registro,
            error=f"Error al guardar inasistencias: {e}"
        ))

# =========================================================================
# 3. 📊 CONSULTAR ASISTENCIA
# =========================================================================

@app.route('/consultar_asistencia', methods=['GET'])
def consultar_asistencia():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')
    id_docente = session.get('id_docente')

    fecha_filtro = request.args.get('fecha', '').strip()
    grado_filtro = request.args.get('grado', '').strip()
    grupo_filtro = request.args.get('grupo', '').strip()
    modalidad_filtro = request.args.get('modalidad', 'General').strip()
    asignatura_filtro = request.args.get('asignatura', '').strip()
    estado_filtro = request.args.get('estado', '').strip()
    estudiante_filtro = request.args.get('estudiante', '').strip()
    if grupo_filtro and not str(grupo_filtro).isdigit():
        _c_norm = obtener_conexion()
        if _c_norm and _c_norm.is_connected():
            _cur_n = _c_norm.cursor(dictionary=True)
            _cur_n.execute("SELECT Gru_Codigo FROM grupo WHERE Gru_NombreGrupo = %s LIMIT 1;", (grupo_filtro,))
            _rg = _cur_n.fetchone()
            _cur_n.close()
            _c_norm.close()
            if _rg:
                grupo_filtro = str(_rg['Gru_Codigo'])

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No hay conexión con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        grupos = []
        if grado_filtro:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_filtro,))
            grupos = cursor.fetchall()
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
            grupos = cursor.fetchall()

        # Validación académica del filtro de asignatura si se seleccionó grado y materia
        lista_estudiantes_filtro = obtener_estudiantes_por_grado_grupo(grado_filtro, grupo_filtro)
        error_validacion = None
        if grado_filtro and asignatura_filtro:
            if not asignatura_valida(grado_filtro, modalidad_filtro, asignatura_filtro):
                error_validacion = f"Aviso de regla académica: La asignatura '{asignatura_filtro}' no corresponde a Grado {grado_filtro}."

        sql = """
            SELECT 
                r.Reg_CodRegistroAsistencia,
                r.Reg_FechaHoraIngreso,
                r.Reg_Observacion,
                e.Est_CodEstudiante,
                e.Est_Nombre,
                e.Est_Apellido,
                g.Gra_NombreGrado,
                gr.Gru_NombreGrupo,
                d.Doc_Nombres,
                d.Doc_Apellidos,
                r.Reg_Jornada,
                r.Reg_Sede,
                COALESCE(r.Reg_Asignatura, a.Asi_NomAsignatura, 'Tecnología e Informática') AS Asi_NomAsignatura
            FROM registroasistencia r
            INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
            LEFT JOIN grado g ON e.Est_Cod_Grado = g.Gra_Codigo
            LEFT JOIN grupo gr ON e.Est_Cod_Grupo = gr.Gru_Codigo
            LEFT JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
            LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            WHERE 1=1
        """
        condiciones = []
        parametros = []

        if rol == 'docente':
            condiciones.append("r.Reg_CodDocente = %s")
            parametros.append(id_docente)

        if fecha_filtro:
            condiciones.append("r.Reg_FechaHoraIngreso LIKE %s")
            parametros.append(f"{fecha_filtro}%")

        if grado_filtro:
            condiciones.append("e.Est_Cod_Grado = %s")
            parametros.append(grado_filtro)

        if grupo_filtro:
            condiciones.append("e.Est_Cod_Grupo = %s")
            parametros.append(grupo_filtro)

        if asignatura_filtro:
            condiciones.append("(r.Reg_Asignatura LIKE %s OR a.Asi_NomAsignatura LIKE %s OR %s LIKE CONCAT('%%', a.Asi_NomAsignatura, '%%'))")
            parametros.extend([f"%{asignatura_filtro}%", f"%{asignatura_filtro}%", asignatura_filtro])

        if estado_filtro:
            condiciones.append("r.Reg_Observacion LIKE %s")
            parametros.append(f"{estado_filtro}%")

        if estudiante_filtro and estudiante_filtro != 'todos':
            if str(estudiante_filtro).isdigit():
                condiciones.append("e.Est_CodEstudiante = %s")
                parametros.append(estudiante_filtro)
            else:
                condiciones.append("""(
                    e.Est_Nombre LIKE %s OR 
                    e.Est_Apellido LIKE %s OR 
                    CONCAT(e.Est_Nombre, ' ', e.Est_Apellido) LIKE %s OR 
                    CONCAT(e.Est_Apellido, ' ', e.Est_Nombre) LIKE %s
                )""")
                term_est = f"%{estudiante_filtro}%"
                parametros.extend([term_est, term_est, term_est, term_est])

        if condiciones:
            sql += " AND " + " AND ".join(condiciones)

        sql += " ORDER BY r.Reg_FechaHoraIngreso DESC, e.Est_Apellido ASC, e.Est_Nombre ASC;"

        cursor.execute(sql, tuple(parametros))
        filas = cursor.fetchall()
        cursor.close()
        conexion.close()

        registros = []
        for fila in filas:
            f_h = str(fila['Reg_FechaHoraIngreso'])
            partes = f_h.split(' ')
            fecha_str = partes[0] if len(partes) > 0 else f_h
            hora_str = partes[1] if len(partes) > 1 else ''

            raw_obs = fila['Reg_Observacion'] or ''
            if ':' in raw_obs:
                st, det = raw_obs.split(':', 1)
                estado_limpio = st.strip()
                obs_limpia = det.strip()
            else:
                estado_limpio = raw_obs.strip()
                obs_limpia = '-'

            registros.append({
                'Reg_CodRegistroAsistencia': fila['Reg_CodRegistroAsistencia'],
                'Fecha': fecha_str,
                'Hora': hora_str,
                'Est_CodEstudiante': fila['Est_CodEstudiante'],
                'Est_Nombre': fila['Est_Nombre'],
                'Est_Apellido': fila['Est_Apellido'],
                'Gra_NombreGrado': fila['Gra_NombreGrado'],
                'Gru_NombreGrupo': fila['Gru_NombreGrupo'],
                'Docente': f"{fila['Doc_Nombres'] or ''} {fila['Doc_Apellidos'] or ''}".strip(),
                'Asignatura': fila['Asi_NomAsignatura'],
                'Estado': estado_limpio,
                'Observacion': obs_limpia
            })

        resumen = {
            'total': len(registros),
            'presentes': sum(1 for r in registros if 'presente' in r['Estado'].lower()),
            'ausentes': sum(1 for r in registros if 'ausente' in r['Estado'].lower()),
            'tardes': sum(1 for r in registros if 'tarde' in r['Estado'].lower())
        }

        filtros = {
            'fecha': fecha_filtro,
            'grado': grado_filtro,
            'grupo': grupo_filtro,
            'modalidad': modalidad_filtro,
            'asignatura': asignatura_filtro,
            'estado': estado_filtro,
            'estudiante': estudiante_filtro
        }

        return render_template(
            'consultar_asistencia.html',
            lista_estudiantes_filtro=lista_estudiantes_filtro,
            registros=registros,
            resumen=resumen,
            grados=grados,
            grupos=grupos,
            modalidades=MODALIDADES_TECNICAS,
            filtros=filtros,
            error_validacion=error_validacion,
            rol=rol,
            usuario=usuario
        )
    except Exception as e:
        print(f"[ERROR CONSULTAR ASISTENCIA]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error=f"Error consultando asistencia: {e}")

# =========================================================================
# 3. 📈 ESTADÍSTICAS
# =========================================================================

@app.route('/estadisticas', methods=['GET'])
def estadisticas():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')
    id_docente = session.get('id_docente')

    fecha_filtro = request.args.get('fecha', '').strip()
    grado_filtro = request.args.get('grado', '').strip()
    grupo_filtro = request.args.get('grupo', '').strip()
    modalidad_filtro = request.args.get('modalidad', 'General').strip()
    asignatura_filtro = request.args.get('asignatura', '').strip()
    estudiante_filtro = request.args.get('estudiante', '').strip()
    if grupo_filtro and not str(grupo_filtro).isdigit():
        _c_norm = obtener_conexion()
        if _c_norm and _c_norm.is_connected():
            _cur_n = _c_norm.cursor(dictionary=True)
            _cur_n.execute("SELECT Gru_Codigo FROM grupo WHERE Gru_NombreGrupo = %s LIMIT 1;", (grupo_filtro,))
            _rg = _cur_n.fetchone()
            _cur_n.close()
            _c_norm.close()
            if _rg:
                grupo_filtro = str(_rg['Gru_Codigo'])

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No hay conexión con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        grupos = []
        if grado_filtro:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_filtro,))
            grupos = cursor.fetchall()
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
            grupos = cursor.fetchall()

        lista_estudiantes_filtro = obtener_estudiantes_por_grado_grupo(grado_filtro, grupo_filtro)

        # Validación académica si se filtró por grado y asignatura
        if grado_filtro and asignatura_filtro and not asignatura_valida(grado_filtro, modalidad_filtro, asignatura_filtro):
            filas = [] # Combinación académica inválida no genera estadísticas
        else:
            sql = """
                SELECT r.Reg_Observacion, e.Est_Cod_Grado, e.Est_Cod_Grupo, r.Reg_FechaHoraIngreso 
                FROM registroasistencia r
                INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
                LEFT JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
                LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
                WHERE 1=1
            """
            condiciones = []
            parametros = []

            if rol == 'docente':
                condiciones.append("r.Reg_CodDocente = %s")
                parametros.append(id_docente)

            if fecha_filtro:
                condiciones.append("r.Reg_FechaHoraIngreso LIKE %s")
                parametros.append(f"{fecha_filtro}%")

            if grado_filtro:
                condiciones.append("e.Est_Cod_Grado = %s")
                parametros.append(grado_filtro)

            if grupo_filtro:
                condiciones.append("e.Est_Cod_Grupo = %s")
                parametros.append(grupo_filtro)

            if asignatura_filtro:
                condiciones.append("(r.Reg_Asignatura LIKE %s OR a.Asi_NomAsignatura LIKE %s OR %s LIKE CONCAT('%%', a.Asi_NomAsignatura, '%%'))")
                parametros.extend([f"%{asignatura_filtro}%", f"%{asignatura_filtro}%", asignatura_filtro])

            if estudiante_filtro and estudiante_filtro != 'todos':
                if str(estudiante_filtro).isdigit():
                    condiciones.append("e.Est_CodEstudiante = %s")
                    parametros.append(estudiante_filtro)
                else:
                    condiciones.append("""(
                        e.Est_Nombre LIKE %s OR 
                        e.Est_Apellido LIKE %s OR 
                        CONCAT(e.Est_Nombre, ' ', e.Est_Apellido) LIKE %s OR 
                        CONCAT(e.Est_Apellido, ' ', e.Est_Nombre) LIKE %s
                    )""")
                    term_est = f"%{estudiante_filtro}%"
                    parametros.extend([term_est, term_est, term_est, term_est])

            if condiciones:
                sql += " AND " + " AND ".join(condiciones)

            cursor.execute(sql, tuple(parametros))
            filas = cursor.fetchall()

        # Conteo institucional de estudiantes (o por grado/grupo)
        total_estudiantes = 0
        try:
            sql_est_count = "SELECT COUNT(*) AS total_est FROM estudiantes WHERE 1=1"
            params_est_count = []
            if grado_filtro:
                sql_est_count += " AND Est_Cod_Grado = %s"
                params_est_count.append(grado_filtro)
            if grupo_filtro:
                sql_est_count += " AND Est_Cod_Grupo = %s"
                params_est_count.append(grupo_filtro)
            cursor.execute(sql_est_count, tuple(params_est_count))
            res_c = cursor.fetchone()
            if res_c:
                total_estudiantes = res_c['total_est']
        except Exception:
            total_estudiantes = len(lista_estudiantes_filtro)

        cursor.close()
        conexion.close()

        total = len(filas)
        presentes = sum(1 for f in filas if 'presente' in str(f['Reg_Observacion']).lower())
        ausentes = sum(1 for f in filas if 'ausente' in str(f['Reg_Observacion']).lower())
        tardes = sum(1 for f in filas if 'tarde' in str(f['Reg_Observacion']).lower())

        pct_presentes = round((presentes / total * 100), 1) if total > 0 else 0.0
        pct_ausentes = round((ausentes / total * 100), 1) if total > 0 else 0.0
        pct_tardes = round((tardes / total * 100), 1) if total > 0 else 0.0

        estudiante_nom_filtro = estudiante_filtro
        if estudiante_filtro and estudiante_filtro != 'todos':
            for e_obj in lista_estudiantes_filtro:
                if str(e_obj['Est_CodEstudiante']) == str(estudiante_filtro):
                    estudiante_nom_filtro = f"{e_obj['Est_Apellido']}, {e_obj['Est_Nombre']}"
                    break

        totales = {
            'total_estudiantes': total_estudiantes,
            'total': total,
            'presentes': presentes,
            'ausentes': ausentes,
            'tardes': tardes
        }
        porcentajes = {
            'presentes': pct_presentes,
            'ausentes': pct_ausentes,
            'tardes': pct_tardes
        }
        filtros = {
            'fecha': fecha_filtro,
            'grado': grado_filtro,
            'grupo': grupo_filtro,
            'modalidad': modalidad_filtro,
            'asignatura': asignatura_filtro,
            'estudiante': estudiante_filtro
        }

        return render_template(
            'estadisticas.html',
            lista_estudiantes_filtro=lista_estudiantes_filtro,
            estudiante_nom_filtro=estudiante_nom_filtro,
            totales=totales,
            porcentajes=porcentajes,
            grados=grados,
            grupos=grupos,
            modalidades=MODALIDADES_TECNICAS,
            filtros=filtros,
            rol=rol,
            usuario=usuario
        )
    except Exception as e:
        print(f"[ERROR ESTADISTICAS]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error=f"Error en estadísticas: {e}")

# =========================================================================
# 4. 📄 REPORTE DE ASISTENCIA
# =========================================================================

@app.route('/reporte', methods=['GET'])
def reporte():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')
    id_docente = session.get('id_docente')

    fecha_filtro = request.args.get('fecha', '').strip()
    grado_filtro = request.args.get('grado', '').strip()
    grupo_filtro = request.args.get('grupo', '').strip()
    modalidad_filtro = request.args.get('modalidad', 'General').strip()
    asignatura_filtro = request.args.get('asignatura', '').strip()
    estado_filtro = request.args.get('estado', '').strip()
    estudiante_filtro = request.args.get('estudiante', '').strip()
    if grupo_filtro and not str(grupo_filtro).isdigit():
        _c_norm = obtener_conexion()
        if _c_norm and _c_norm.is_connected():
            _cur_n = _c_norm.cursor(dictionary=True)
            _cur_n.execute("SELECT Gru_Codigo FROM grupo WHERE Gru_NombreGrupo = %s LIMIT 1;", (grupo_filtro,))
            _rg = _cur_n.fetchone()
            _cur_n.close()
            _c_norm.close()
            if _rg:
                grupo_filtro = str(_rg['Gru_Codigo'])

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No hay conexión con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        grupos = []
        if grado_filtro:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_filtro,))
            grupos = cursor.fetchall()
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
            grupos = cursor.fetchall()

        lista_estudiantes_filtro = obtener_estudiantes_por_grado_grupo(grado_filtro, grupo_filtro)

        # Validación académica estricta: Grado 10 + Contable + Tecnología es inválido
        invalida = False
        if grado_filtro and asignatura_filtro and not asignatura_valida(grado_filtro, modalidad_filtro, asignatura_filtro):
            invalida = True

        if invalida:
            filas = []
        else:
            sql = """
                SELECT 
                    r.Reg_CodRegistroAsistencia,
                    r.Reg_FechaHoraIngreso,
                    r.Reg_Observacion,
                    e.Est_CodEstudiante,
                    e.Est_Nombre,
                    e.Est_Apellido,
                    g.Gra_NombreGrado,
                    gr.Gru_NombreGrupo,
                    d.Doc_Nombres,
                    d.Doc_Apellidos,
                    r.Reg_Jornada,
                    r.Reg_Sede,
                    COALESCE(r.Reg_Asignatura, a.Asi_NomAsignatura, 'Tecnología e Informática') AS Asi_NomAsignatura
                FROM registroasistencia r
                INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
                LEFT JOIN grado g ON e.Est_Cod_Grado = g.Gra_Codigo
                LEFT JOIN grupo gr ON e.Est_Cod_Grupo = gr.Gru_Codigo
                LEFT JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
                LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
                WHERE 1=1
            """
            condiciones = []
            parametros = []

            if rol == 'docente':
                condiciones.append("r.Reg_CodDocente = %s")
                parametros.append(id_docente)

            if fecha_filtro:
                condiciones.append("r.Reg_FechaHoraIngreso LIKE %s")
                parametros.append(f"{fecha_filtro}%")

            if grado_filtro:
                condiciones.append("e.Est_Cod_Grado = %s")
                parametros.append(grado_filtro)

            if grupo_filtro:
                condiciones.append("e.Est_Cod_Grupo = %s")
                parametros.append(grupo_filtro)

            if asignatura_filtro:
                condiciones.append("(r.Reg_Asignatura LIKE %s OR a.Asi_NomAsignatura LIKE %s OR %s LIKE CONCAT('%%', a.Asi_NomAsignatura, '%%'))")
                parametros.extend([f"%{asignatura_filtro}%", f"%{asignatura_filtro}%", asignatura_filtro])

            if estado_filtro:
                condiciones.append("r.Reg_Observacion LIKE %s")
                parametros.append(f"{estado_filtro}%")

            if estudiante_filtro and estudiante_filtro != 'todos':
                if str(estudiante_filtro).isdigit():
                    condiciones.append("e.Est_CodEstudiante = %s")
                    parametros.append(estudiante_filtro)
                else:
                    condiciones.append("""(
                        e.Est_Nombre LIKE %s OR 
                        e.Est_Apellido LIKE %s OR 
                        CONCAT(e.Est_Nombre, ' ', e.Est_Apellido) LIKE %s OR 
                        CONCAT(e.Est_Apellido, ' ', e.Est_Nombre) LIKE %s
                    )""")
                    term_est = f"%{estudiante_filtro}%"
                    parametros.extend([term_est, term_est, term_est, term_est])

            if condiciones:
                sql += " AND " + " AND ".join(condiciones)

            sql += " ORDER BY r.Reg_FechaHoraIngreso DESC, e.Est_Apellido ASC, e.Est_Nombre ASC;"

            cursor.execute(sql, tuple(parametros))
            filas = cursor.fetchall()

        # Conteo institucional de estudiantes (o por grado/grupo)
        total_estudiantes = 0
        try:
            sql_est_count = "SELECT COUNT(*) AS total_est FROM estudiantes WHERE 1=1"
            params_est_count = []
            if grado_filtro:
                sql_est_count += " AND Est_Cod_Grado = %s"
                params_est_count.append(grado_filtro)
            if grupo_filtro:
                sql_est_count += " AND Est_Cod_Grupo = %s"
                params_est_count.append(grupo_filtro)
            cursor.execute(sql_est_count, tuple(params_est_count))
            res_c = cursor.fetchone()
            if res_c:
                total_estudiantes = res_c['total_est']
        except Exception:
            total_estudiantes = len(lista_estudiantes_filtro)

        cursor.close()
        conexion.close()

        registros = []
        for fila in filas:
            f_h = str(fila['Reg_FechaHoraIngreso'])
            partes = f_h.split(' ')
            fecha_str = partes[0] if len(partes) > 0 else f_h
            hora_str = partes[1] if len(partes) > 1 else ''

            raw_obs = fila['Reg_Observacion'] or ''
            if ':' in raw_obs:
                st, det = raw_obs.split(':', 1)
                estado_limpio = st.strip()
                obs_limpia = det.strip()
            else:
                estado_limpio = raw_obs.strip()
                obs_limpia = '-'

            jornada_val = fila.get('Reg_Jornada') or 'Mañana'
            if 'Ma' in jornada_val and 'ana' in jornada_val:
                jornada_val = 'Mañana'

            registros.append({
                'Reg_CodRegistroAsistencia': fila['Reg_CodRegistroAsistencia'],
                'Fecha': fecha_str,
                'Hora': hora_str,
                'FechaHora': f_h,
                'Est_CodEstudiante': fila['Est_CodEstudiante'],
                'Est_Nombre': fila['Est_Nombre'],
                'Est_Apellido': fila['Est_Apellido'],
                'Gra_NombreGrado': fila['Gra_NombreGrado'],
                'Gru_NombreGrupo': fila['Gru_NombreGrupo'],
                'Docente': f"{fila['Doc_Nombres'] or ''} {fila['Doc_Apellidos'] or ''}".strip(),
                'Asignatura': fila['Asi_NomAsignatura'],
                'Jornada': jornada_val,
                'Sede': fila.get('Reg_Sede') or 'Sede Central',
                'Estado': estado_limpio,
                'Observacion': obs_limpia
            })

        resumen = {
            'total_estudiantes': total_estudiantes,
            'total': len(registros),
            'presentes': sum(1 for r in registros if 'presente' in r['Estado'].lower()),
            'ausentes': sum(1 for r in registros if 'ausente' in r['Estado'].lower()),
            'tardes': sum(1 for r in registros if 'tarde' in r['Estado'].lower())
        }

        filtros = {
            'fecha': fecha_filtro,
            'grado': grado_filtro,
            'grupo': grupo_filtro,
            'modalidad': modalidad_filtro,
            'asignatura': asignatura_filtro,
            'estado': estado_filtro,
            'estudiante': estudiante_filtro
        }

        grado_nombre_sel = ''
        if grado_filtro:
            for g in grados:
                if str(g['Gra_Codigo']) == str(grado_filtro):
                    grado_nombre_sel = f"Grado {g['Gra_NombreGrado']}" if g['Gra_Codigo'] != 0 else g['Gra_NombreGrado']
                    break

        grupo_nombre_sel = ''
        if grupo_filtro:
            for gr in grupos:
                if str(gr['Gru_Codigo']) == str(grupo_filtro):
                    grupo_nombre_sel = gr['Gru_NombreGrupo']
                    break

        estudiante_nom_filtro = estudiante_filtro
        if estudiante_filtro and estudiante_filtro != 'todos':
            for e_obj in lista_estudiantes_filtro:
                if str(e_obj['Est_CodEstudiante']) == str(estudiante_filtro):
                    estudiante_nom_filtro = f"{e_obj['Est_Apellido']}, {e_obj['Est_Nombre']}"
                    break

        fecha_emision = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return render_template(
            'reporte.html',
            lista_estudiantes_filtro=lista_estudiantes_filtro,
            estudiante_nom_filtro=estudiante_nom_filtro,
            registros=registros,
            resumen=resumen,
            grados=grados,
            grupos=grupos,
            modalidades=MODALIDADES_TECNICAS,
            filtros=filtros,
            combinacion_invalida=invalida,
            grado_nombre_sel=grado_nombre_sel,
            grupo_nombre_sel=grupo_nombre_sel,
            fecha_emision=fecha_emision,
            rol=rol,
            usuario=usuario
        )
    except Exception as e:
        print(f"[ERROR REPORTE]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error=f"Error generando reporte: {e}")

# =========================================================================
# 5. ⚙️ GESTIÓN Y ACTUALIZACIÓN DE ESTUDIANTES (COORDINACIÓN Y ÁREA TECNOLOGÍA)
# =========================================================================

@app.route('/gestion_estudiantes', methods=['GET'])
def gestion_estudiantes():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    rol = session.get('rol')
    solo_lectura = False

    if rol == 'rectoria':
        solo_lectura = True
    elif rol == 'coordinador':
        solo_lectura = False
    elif rol == 'docente':
        if not tiene_permiso_gestion_estudiantes():
            return render_template(
                'docente.html',
                usuario=session.get('usuario'),
                rol='docente',
                puede_gestionar_estudiantes=False,
                error="No tienes autorización para gestionar matrículas. Solicita permiso a la coordinación"
            )
    else:
        return redirect(url_for('login'))

    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return render_template(
            'gestion_estudiantes.html',
            error="No hay conexión con la base de datos MySQL.",
            usuario=session.get('usuario'),
            rol=rol,
            solo_lectura=solo_lectura,
            estudiantes=[],
            filtros={},
            anio_activo=2026,
            grados=[],
            grupos=[],
            jornadas=JORNADAS_DISPONIBLES,
            sedes=SEDES_DISPONIBLES,
            anios_disponibles=[2024, 2025, 2026, 2027],
            total_filtrados=0,
            total_activos=0,
            total_retirados=0,
            total_graduados=0
        )

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo, Gru_Cod_Grado FROM grupo ORDER BY Gru_Codigo;")
        grupos = cursor.fetchall()

        cursor.execute("SELECT Sed_CodigoSede, Sed_NomSede FROM sedes ORDER BY Sed_CodigoSede;")
        sedes_db = [s['Sed_NomSede'] for s in cursor.fetchall()]
        sedes = sedes_db if sedes_db else SEDES_DISPONIBLES

        anio_activo = obtener_anio_lectivo_activo_bd()

        # Filtros recibidos
        q = request.args.get('q', request.args.get('busqueda', '')).strip()
        grado_sel = request.args.get('grado', '').strip()
        grupo_sel = request.args.get('grupo', '').strip()
        jornada_sel = request.args.get('jornada', '').strip()
        sede_sel = request.args.get('sede', '').strip()
        estado_sel = request.args.get('estado', '').strip()
        anio_sel = request.args.get('anio', '').strip()
        mensaje = request.args.get('mensaje', '').strip()
        error = request.args.get('error', '').strip()

        # Construcción de consulta SQL
        sql = """
            SELECT e.Est_CodEstudiante, e.Est_Nombre, e.Est_Apellido, e.Est_Cod_Grado, e.Est_Cod_Grupo,
                   e.Est_Jornada, e.Est_Correo, e.Est_Telefono, e.Est_Estado, e.Est_AnioLectivo,
                   g.Gra_NombreGrado, grp.Gru_NombreGrupo, s.Sed_NomSede
            FROM estudiantes e
            LEFT JOIN grado g ON e.Est_Cod_Grado = g.Gra_Codigo
            LEFT JOIN grupo grp ON e.Est_Cod_Grupo = grp.Gru_Codigo
            LEFT JOIN sedes s ON e.Est_Cod_SedeEstudiantil = s.Sed_CodigoSede
            WHERE 1=1
        """
        params = []
        if q:
            sql += " AND (e.Est_Nombre LIKE %s OR e.Est_Apellido LIKE %s OR CONCAT(e.Est_Nombre, ' ', e.Est_Apellido) LIKE %s OR CONCAT(e.Est_Apellido, ' ', e.Est_Nombre) LIKE %s)"
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"])
        if grado_sel:
            sql += " AND e.Est_Cod_Grado = %s"
            params.append(grado_sel)
        if grupo_sel:
            sql += " AND (e.Est_Cod_Grupo = %s OR grp.Gru_NombreGrupo = %s)"
            params.extend([grupo_sel, grupo_sel])
        if jornada_sel:
            sql += " AND e.Est_Jornada LIKE %s"
            params.append(f"{jornada_sel}%")
        if sede_sel:
            sql += " AND (s.Sed_NomSede LIKE %s OR %s LIKE CONCAT('%%', s.Sed_NomSede, '%%'))"
            params.extend([f"%{sede_sel}%", sede_sel])
        if estado_sel:
            sql += " AND e.Est_Estado = %s"
            params.append(estado_sel)
        if anio_sel:
            sql += " AND e.Est_AnioLectivo = %s"
            params.append(int(anio_sel))

        sql += " ORDER BY e.Est_Apellido ASC, e.Est_Nombre ASC;"
        cursor.execute(sql, tuple(params))
        estudiantes = cursor.fetchall()

        # Determinar años disponibles en la base de datos
        cursor.execute("SELECT DISTINCT Est_AnioLectivo FROM estudiantes WHERE Est_AnioLectivo IS NOT NULL ORDER BY Est_AnioLectivo DESC;")
        anios_rows = cursor.fetchall()
        anios_disponibles = [r['Est_AnioLectivo'] for r in anios_rows if r['Est_AnioLectivo']]
        if anio_activo not in anios_disponibles:
            anios_disponibles.append(anio_activo)
        anios_disponibles.sort(reverse=True)

        cursor.close()
        conn.close()

        total_filtrados = len(estudiantes)
        total_activos = sum(1 for e in estudiantes if (e['Est_Estado'] or 'Activo') == 'Activo')
        total_retirados = sum(1 for e in estudiantes if (e['Est_Estado'] or '') == 'Retirado')
        total_graduados = sum(1 for e in estudiantes if (e['Est_Estado'] or '') == 'Graduado')

        filtros = {
            'q': q,
            'grado': grado_sel,
            'grupo': grupo_sel,
            'jornada': jornada_sel,
            'sede': sede_sel,
            'estado': estado_sel,
            'anio': anio_sel
        }

        return render_template(
            'gestion_estudiantes.html',
            estudiantes=estudiantes,
            filtros=filtros,
            anio_activo=anio_activo,
            grados=grados,
            grupos=grupos,
            jornadas=JORNADAS_DISPONIBLES,
            sedes=sedes,
            anios_disponibles=anios_disponibles,
            total_filtrados=total_filtrados,
            total_activos=total_activos,
            total_retirados=total_retirados,
            total_graduados=total_graduados,
            solo_lectura=solo_lectura,
            mensaje=mensaje,
            error=error,
            usuario=session.get('usuario'),
            rol=rol
        )
    except Exception as e:
        print(f"[ERROR GESTION ESTUDIANTES]: {e}")
        if conn and conn.is_connected():
            conn.close()
        return render_template('login.html', error=f"Error en gestión de estudiantes: {e}")

@app.route('/gestion_estudiantes/nuevo', methods=['GET', 'POST'])
def nuevo_estudiante():
    if not tiene_permiso_gestion_estudiantes():
        return redirect(url_for('docente', error='No tienes autorización para gestionar matrículas. Solicita permiso a la coordinación') if session.get('rol') == 'docente' else url_for('login'))

    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return redirect(url_for('gestion_estudiantes', error="Sin conexión a la base de datos."))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()
        cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo, Gru_Cod_Grado FROM grupo ORDER BY Gru_Codigo;")
        grupos = cursor.fetchall()
        cursor.execute("SELECT Sed_NomSede FROM sedes ORDER BY Sed_CodigoSede;")
        sedes = [s['Sed_NomSede'] for s in cursor.fetchall()] or SEDES_DISPONIBLES
        anio_activo = obtener_anio_lectivo_activo_bd()

        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            apellido = request.form.get('apellido', '').strip()
            grado = request.form.get('grado', '').strip()
            grupo = request.form.get('grupo', '').strip()
            jornada = request.form.get('jornada', 'Mañana').strip()
            sede_nom = request.form.get('sede', 'Sede Central').strip()
            anio = request.form.get('anio', str(anio_activo)).strip()
            estado = request.form.get('estado', 'Activo').strip()
            correo = request.form.get('correo', '').strip()
            telefono = request.form.get('telefono', '').strip()

            if not nombre or not apellido or not grado or not grupo:
                cursor.close()
                conn.close()
                return render_template(
                    'estudiante_formulario.html',
                    es_edicion=False,
                    estudiante={},
                    grados=grados,
                    grupos=grupos,
                    sedes=sedes,
                    jornadas=JORNADAS_DISPONIBLES,
                    anio_activo=anio_activo,
                    usuario=session.get('usuario'),
                    rol=session.get('rol'),
                    error="Todos los campos marcados con asterisco (*) son obligatorios."
                )

            # Buscar siguiente ID único para el estudiante
            cursor.execute("SELECT COALESCE(MAX(Est_CodEstudiante), 1000) + 1 AS next_id FROM estudiantes;")
            next_id = cursor.fetchone()['next_id']

            # Resolver código numérico de sede si aplica
            sede_cod = 1
            cursor.execute("SELECT Sed_CodigoSede FROM sedes WHERE Sed_NomSede = %s LIMIT 1;", (sede_nom,))
            r_sed = cursor.fetchone()
            if r_sed:
                sede_cod = r_sed['Sed_CodigoSede']

            # Resolver código numérico de grupo si viene como nombre
            grupo_id = grupo
            if not str(grupo).isdigit():
                cursor.execute("SELECT Gru_Codigo FROM grupo WHERE Gru_NombreGrupo = %s LIMIT 1;", (grupo,))
                r_grp = cursor.fetchone()
                if r_grp:
                    grupo_id = r_grp['Gru_Codigo']

            sql_ins = """
                INSERT INTO estudiantes (
                    Est_CodEstudiante, Est_Nombre, Est_Apellido, Est_Cod_Grado, Est_Cod_Grupo,
                    Est_Jornada, Est_Cod_SedeEstudiantil, Est_AnioLectivo, Est_Estado,
                    Est_Correo, Est_Telefono, Est_Direcion, Est_ObservacionMedica, Est_Gereno
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '', '', 'No especificado');
            """
            cursor.execute(sql_ins, (
                next_id, nombre, apellido, grado, grupo_id,
                jornada, sede_cod, int(anio) if str(anio).isdigit() else anio_activo, estado,
                correo, telefono if str(telefono).isdigit() else None
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('gestion_estudiantes', mensaje=f"Estudiante '{apellido}, {nombre}' creado exitosamente."))

        cursor.close()
        conn.close()
        return render_template(
            'estudiante_formulario.html',
            es_edicion=False,
            estudiante={},
            grados=grados,
            grupos=grupos,
            sedes=sedes,
            jornadas=JORNADAS_DISPONIBLES,
            anio_activo=anio_activo,
            usuario=session.get('usuario'),
            rol=session.get('rol')
        )
    except Exception as e:
        print(f"[ERROR NUEVO ESTUDIANTE]: {e}")
        if conn and conn.is_connected():
            conn.close()
        return redirect(url_for('gestion_estudiantes', error=f"Error al registrar estudiante: {e}"))

@app.route('/gestion_estudiantes/editar/<int:id_estudiante>', methods=['GET', 'POST'])
def editar_estudiante(id_estudiante):
    if not tiene_permiso_gestion_estudiantes():
        return redirect(url_for('docente', error='No tienes autorización para gestionar matrículas. Solicita permiso a la coordinación') if session.get('rol') == 'docente' else url_for('login'))

    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return redirect(url_for('gestion_estudiantes', error="Sin conexión a la base de datos."))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()
        cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo, Gru_Cod_Grado FROM grupo ORDER BY Gru_Codigo;")
        grupos = cursor.fetchall()
        cursor.execute("SELECT Sed_NomSede FROM sedes ORDER BY Sed_CodigoSede;")
        sedes = [s['Sed_NomSede'] for s in cursor.fetchall()] or SEDES_DISPONIBLES
        anio_activo = obtener_anio_lectivo_activo_bd()

        cursor.execute("""
            SELECT e.*, s.Sed_NomSede 
            FROM estudiantes e 
            LEFT JOIN sedes s ON e.Est_Cod_SedeEstudiantil = s.Sed_CodigoSede
            WHERE e.Est_CodEstudiante = %s;
        """, (id_estudiante,))
        estudiante = cursor.fetchone()

        if not estudiante:
            cursor.close()
            conn.close()
            return redirect(url_for('gestion_estudiantes', error="Estudiante no encontrado."))

        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            apellido = request.form.get('apellido', '').strip()
            grado = request.form.get('grado', '').strip()
            grupo = request.form.get('grupo', '').strip()
            jornada = request.form.get('jornada', 'Mañana').strip()
            sede_nom = request.form.get('sede', 'Sede Central').strip()
            anio = request.form.get('anio', str(estudiante.get('Est_AnioLectivo') or anio_activo)).strip()
            estado = request.form.get('estado', 'Activo').strip()
            correo = request.form.get('correo', '').strip()
            telefono = request.form.get('telefono', '').strip()

            if not nombre or not apellido or not grado or not grupo:
                cursor.close()
                conn.close()
                return render_template(
                    'estudiante_formulario.html',
                    es_edicion=True,
                    estudiante=estudiante,
                    grados=grados,
                    grupos=grupos,
                    sedes=sedes,
                    jornadas=JORNADAS_DISPONIBLES,
                    anio_activo=anio_activo,
                    usuario=session.get('usuario'),
                    rol=session.get('rol'),
                    error="Todos los campos marcados con asterisco (*) son obligatorios."
                )

            # Resolver código numérico de sede si aplica
            sede_cod = estudiante.get('Est_Cod_SedeEstudiantil') or 1
            cursor.execute("SELECT Sed_CodigoSede FROM sedes WHERE Sed_NomSede = %s LIMIT 1;", (sede_nom,))
            r_sed = cursor.fetchone()
            if r_sed:
                sede_cod = r_sed['Sed_CodigoSede']

            # Resolver código numérico de grupo si viene como nombre
            grupo_id = grupo
            if not str(grupo).isdigit():
                cursor.execute("SELECT Gru_Codigo FROM grupo WHERE Gru_NombreGrupo = %s LIMIT 1;", (grupo,))
                r_grp = cursor.fetchone()
                if r_grp:
                    grupo_id = r_grp['Gru_Codigo']

            sql_upd = """
                UPDATE estudiantes 
                SET Est_Nombre = %s, Est_Apellido = %s, Est_Cod_Grado = %s, Est_Cod_Grupo = %s,
                    Est_Jornada = %s, Est_Cod_SedeEstudiantil = %s, Est_AnioLectivo = %s,
                    Est_Estado = %s, Est_Correo = %s, Est_Telefono = %s
                WHERE Est_CodEstudiante = %s;
            """
            cursor.execute(sql_upd, (
                nombre, apellido, grado, grupo_id,
                jornada, sede_cod, int(anio) if str(anio).isdigit() else anio_activo,
                estado, correo, telefono if str(telefono).isdigit() else None,
                id_estudiante
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('gestion_estudiantes', mensaje=f"Estudiante '{apellido}, {nombre}' actualizado correctamente (Grado {grado}, Grupo {grupo}, Año {anio})."))

        cursor.close()
        conn.close()
        return render_template(
            'estudiante_formulario.html',
            es_edicion=True,
            estudiante=estudiante,
            grados=grados,
            grupos=grupos,
            sedes=sedes,
            jornadas=JORNADAS_DISPONIBLES,
            anio_activo=anio_activo,
            usuario=session.get('usuario'),
            rol=session.get('rol')
        )
    except Exception as e:
        print(f"[ERROR EDITAR ESTUDIANTE]: {e}")
        if conn and conn.is_connected():
            conn.close()
        return redirect(url_for('gestion_estudiantes', error=f"Error al editar estudiante: {e}"))

@app.route('/gestion_estudiantes/cambiar_estado/<int:id_estudiante>', methods=['POST'])
def cambiar_estado_estudiante(id_estudiante):
    if not tiene_permiso_gestion_estudiantes():
        return redirect(url_for('docente', error='No tienes autorización para gestionar matrículas. Solicita permiso a la coordinación') if session.get('rol') == 'docente' else url_for('login'))

    nuevo_estado = request.form.get('nuevo_estado', 'Activo').strip()
    if nuevo_estado not in ['Activo', 'Retirado', 'Trasladado', 'Graduado']:
        nuevo_estado = 'Activo'

    conn = obtener_conexion()
    if conn and conn.is_connected():
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("UPDATE estudiantes SET Est_Estado = %s WHERE Est_CodEstudiante = %s;", (nuevo_estado, id_estudiante))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('gestion_estudiantes', mensaje=f"Estado del estudiante actualizado a '{nuevo_estado}'."))
        except Exception as e:
            print(f"[ERROR CAMBIO ESTADO]: {e}")
            if conn and conn.is_connected():
                conn.close()
    return redirect(url_for('gestion_estudiantes', error="No se pudo actualizar el estado del estudiante."))

@app.route('/gestion_estudiantes/plantilla', methods=['GET'])
def descargar_plantilla_estudiantes():
    output = io.StringIO()
    # Escribir BOM UTF-8 para compatibilidad nativa con Excel en español
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=',')
    writer.writerow(['Nombres', 'Apellidos', 'Grado', 'Grupo', 'Jornada', 'Sede', 'Año', 'Estado'])
    writer.writerow(['Juan Camilo', 'Pérez Gómez', '11', '11-6', 'Tarde', 'Sede Central', '2026', 'Activo'])
    writer.writerow(['María Alejandra', 'López Silva', '10', '10-1', 'Mañana', 'Sede Central', '2026', 'Activo'])
    writer.writerow(['Carlos Andrés', 'Martínez Díaz', '9', '9-1', 'Mañana', 'Sede Central', '2026', 'Activo'])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=plantilla_estudiantes_asistec.csv"}
    )

@app.route('/gestion_estudiantes/importar', methods=['GET'])
def importar_estudiantes():
    if not tiene_permiso_gestion_estudiantes():
        return redirect(url_for('docente', error='No tienes autorización para gestionar matrículas. Solicita permiso a la coordinación') if session.get('rol') == 'docente' else url_for('login'))
    session.pop('import_preview_rows', None)
    return render_template('importar_estudiantes.html', preview=None, usuario=session.get('usuario'), rol=session.get('rol'))

@app.route('/gestion_estudiantes/importar/preview', methods=['POST'])
def preview_importar_estudiantes():
    if not tiene_permiso_gestion_estudiantes():
        return redirect(url_for('docente', error='No tienes autorización para gestionar matrículas. Solicita permiso a la coordinación') if session.get('rol') == 'docente' else url_for('login'))

    archivo = request.files.get('archivo')
    if not archivo or not archivo.filename:
        return render_template('importar_estudiantes.html', preview=None, error="Por favor selecciona un archivo para importar.", usuario=session.get('usuario'), rol=session.get('rol'))

    nombre_archivo = archivo.filename.lower()
    filas_brutas = []

    try:
        if nombre_archivo.endswith('.csv'):
            contenido = archivo.read().decode('utf-8-sig', errors='replace')
            # Detectar delimitador (coma o punto y coma)
            delimiter = ';' if ';' in contenido.splitlines()[0] else ','
            reader = csv.reader(io.StringIO(contenido), delimiter=delimiter)
            filas_brutas = [r for r in reader if any(cell.strip() for cell in r)]
        elif nombre_archivo.endswith('.xlsx'):
            import openpyxl
            wb = openpyxl.load_workbook(filename=io.BytesIO(archivo.read()), data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(values_only=True):
                if any(row):
                    filas_brutas.append([str(c).strip() if c is not None else '' for c in row])
        else:
            return render_template('importar_estudiantes.html', preview=None, error="Formato no soportado. Debe ser un archivo .xlsx o .csv.", usuario=session.get('usuario'), rol=session.get('rol'))
    except Exception as e:
        return render_template('importar_estudiantes.html', preview=None, error=f"Error al leer el archivo: {e}", usuario=session.get('usuario'), rol=session.get('rol'))

    if len(filas_brutas) < 2:
        return render_template('importar_estudiantes.html', preview=None, error="El archivo no contiene filas de datos o está vacío.", usuario=session.get('usuario'), rol=session.get('rol'))

    # Analizar encabezados
    encabezados = [c.lower().strip() for c in filas_brutas[0]]
    idx_nom, idx_ape, idx_gra, idx_grp, idx_jor, idx_sed, idx_ani, idx_est = -1, -1, -1, -1, -1, -1, -1, -1
    for i, h in enumerate(encabezados):
        if 'nom' in h and 'completo' not in h: idx_nom = i
        elif 'completo' in h: idx_nom = i
        elif 'ape' in h: idx_ape = i
        elif 'gra' in h: idx_gra = i
        elif 'gru' in h: idx_grp = i
        elif 'jor' in h: idx_jor = i
        elif 'sed' in h: idx_sed = i
        elif 'a' in h and ('no' in h or 'ñ' in h or 'anio' in h): idx_ani = i
        elif 'est' in h: idx_est = i

    # Asignaciones por defecto si no se detectaron nombres específicos
    if idx_nom == -1 and len(encabezados) > 0: idx_nom = 0
    if idx_ape == -1 and len(encabezados) > 1: idx_ape = 1
    if idx_gra == -1 and len(encabezados) > 2: idx_gra = 2
    if idx_grp == -1 and len(encabezados) > 3: idx_grp = 3
    if idx_jor == -1 and len(encabezados) > 4: idx_jor = 4
    if idx_sed == -1 and len(encabezados) > 5: idx_sed = 5
    if idx_ani == -1 and len(encabezados) > 6: idx_ani = 6

    conn = obtener_conexion()
    estudiantes_db = []
    if conn and conn.is_connected():
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT Est_Nombre, Est_Apellido, Est_Cod_Grado, Est_Cod_Grupo FROM estudiantes;")
        estudiantes_db = cur.fetchall()
        cur.close()
        conn.close()

    nombres_db_set = {
        (normalizar_nombre_asignatura(e['Est_Nombre']), normalizar_nombre_asignatura(e['Est_Apellido']))
        for e in estudiantes_db
    }

    filas_preview = []
    total_duplicados = 0
    total_nuevos = 0

    anio_activo = obtener_anio_lectivo_activo_bd()

    for idx, r in enumerate(filas_brutas[1:]):
        nom = r[idx_nom].strip() if idx_nom >= 0 and idx_nom < len(r) else ''
        ape = r[idx_ape].strip() if idx_ape >= 0 and idx_ape < len(r) else ''
        gra = r[idx_gra].strip() if idx_gra >= 0 and idx_gra < len(r) else '11'
        grp = r[idx_grp].strip() if idx_grp >= 0 and idx_grp < len(r) else '11-6'
        jor = r[idx_jor].strip() if idx_jor >= 0 and idx_jor < len(r) else 'Mañana'
        sed = r[idx_sed].strip() if idx_sed >= 0 and idx_sed < len(r) else 'Sede Central'
        ani = r[idx_ani].strip() if idx_ani >= 0 and idx_ani < len(r) else str(anio_activo)
        st = r[idx_est].strip() if idx_est >= 0 and idx_est < len(r) else 'Activo'

        if not nom and not ape:
            continue

        # Si el nombre viene completo en una sola celda
        if nom and not ape and ',' in nom:
            partes = nom.split(',', 1)
            ape, nom = partes[0].strip(), partes[1].strip()

        # Detección de duplicado
        norm_key = (normalizar_nombre_asignatura(nom), normalizar_nombre_asignatura(ape))
        es_dup = norm_key in nombres_db_set
        if es_dup:
            total_duplicados += 1
        else:
            total_nuevos += 1

        filas_preview.append({
            'nombre': nom,
            'apellido': ape,
            'grado': gra,
            'grupo_nom': grp,
            'jornada': jor,
            'sede': sed,
            'anio': int(ani) if str(ani).isdigit() else anio_activo,
            'estado': st or 'Activo',
            'es_duplicado': es_dup,
            'error_val': None
        })

    session['import_preview_rows'] = filas_preview
    token_preview = datetime.now().strftime("%Y%m%d%H%M%S")

    return render_template(
        'importar_estudiantes.html',
        preview=filas_preview,
        total_nuevos=total_nuevos,
        total_duplicados=total_duplicados,
        token_preview=token_preview,
        usuario=session.get('usuario'),
        rol=session.get('rol')
    )

@app.route('/gestion_estudiantes/importar/confirmar', methods=['POST'])
def confirmar_importar_estudiantes():
    if not tiene_permiso_gestion_estudiantes():
        return redirect(url_for('docente', error='No tienes autorización para gestionar matrículas. Solicita permiso a la coordinación') if session.get('rol') == 'docente' else url_for('login'))

    filas = session.get('import_preview_rows', [])
    if not filas:
        return redirect(url_for('gestion_estudiantes', error="No hay datos en vista previa para importar o la sesión expiró."))

    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return redirect(url_for('gestion_estudiantes', error="Sin conexión a MySQL para guardar los estudiantes."))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COALESCE(MAX(Est_CodEstudiante), 1000) AS max_id FROM estudiantes;")
        curr_id = cursor.fetchone()['max_id']

        cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo;")
        grupos_dict = {str(g['Gru_NombreGrupo']).strip().lower(): g['Gru_Codigo'] for g in cursor.fetchall()}

        cursor.execute("SELECT Sed_CodigoSede, Sed_NomSede FROM sedes;")
        sedes_dict = {str(s['Sed_NomSede']).strip().lower(): s['Sed_CodigoSede'] for s in cursor.fetchall()}

        insertados = 0
        sql_ins = """
            INSERT INTO estudiantes (
                Est_CodEstudiante, Est_Nombre, Est_Apellido, Est_Cod_Grado, Est_Cod_Grupo,
                Est_Jornada, Est_Cod_SedeEstudiantil, Est_AnioLectivo, Est_Estado,
                Est_Correo, Est_Telefono, Est_Direcion, Est_ObservacionMedica, Est_Gereno
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '', '', '', '', 'No especificado');
        """

        for item in filas:
            curr_id += 1
            grp_code = grupos_dict.get(str(item['grupo_nom']).strip().lower(), 1)
            sed_code = sedes_dict.get(str(item['sede']).strip().lower(), 1)
            gra_code = int(item['grado']) if str(item['grado']).isdigit() else 11

            cursor.execute(sql_ins, (
                curr_id, item['nombre'], item['apellido'], gra_code, grp_code,
                item['jornada'], sed_code, item['anio'], item['estado']
            ))
            insertados += 1

        conn.commit()
        cursor.close()
        conn.close()

        session.pop('import_preview_rows', None)
        return redirect(url_for('gestion_estudiantes', mensaje=f"Carga masiva completada exitosamente: {insertados} estudiantes registrados."))
    except Exception as e:
        print(f"[ERROR CONFIRMAR IMPORTACION]: {e}")
        if conn and conn.is_connected():
            conn.close()
        return redirect(url_for('gestion_estudiantes', error=f"Error durante la importación: {e}"))

@app.route('/gestion_estudiantes/exportar', methods=['GET'])
def exportar_estudiantes():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    rol = session.get('rol')
    if rol not in ('coordinador', 'rectoria') and not tiene_permiso_gestion_estudiantes():
        return redirect(url_for('docente', error="Acceso denegado: No tienes autorización para exportar datos de matrícula."))

    conn = obtener_conexion()
    if not conn or not conn.is_connected():
        return "Error: Sin conexión a base de datos.", 500

    try:
        cursor = conn.cursor(dictionary=True)
        q = request.args.get('q', '').strip()
        grado_sel = request.args.get('grado', '').strip()
        grupo_sel = request.args.get('grupo', '').strip()
        jornada_sel = request.args.get('jornada', '').strip()
        sede_sel = request.args.get('sede', '').strip()
        estado_sel = request.args.get('estado', '').strip()
        anio_sel = request.args.get('anio', '').strip()

        sql = """
            SELECT e.Est_CodEstudiante, e.Est_Nombre, e.Est_Apellido, e.Est_Cod_Grado,
                   grp.Gru_NombreGrupo, e.Est_Jornada, s.Sed_NomSede, e.Est_AnioLectivo,
                   e.Est_Estado, e.Est_Correo, e.Est_Telefono
            FROM estudiantes e
            LEFT JOIN grupo grp ON e.Est_Cod_Grupo = grp.Gru_Codigo
            LEFT JOIN sedes s ON e.Est_Cod_SedeEstudiantil = s.Sed_CodigoSede
            WHERE 1=1
        """
        params = []
        if q:
            sql += " AND (e.Est_Nombre LIKE %s OR e.Est_Apellido LIKE %s OR CONCAT(e.Est_Nombre, ' ', e.Est_Apellido) LIKE %s OR CONCAT(e.Est_Apellido, ' ', e.Est_Nombre) LIKE %s)"
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"])
        if grado_sel:
            sql += " AND e.Est_Cod_Grado = %s"
            params.append(grado_sel)
        if grupo_sel:
            sql += " AND (e.Est_Cod_Grupo = %s OR grp.Gru_NombreGrupo = %s)"
            params.extend([grupo_sel, grupo_sel])
        if jornada_sel:
            sql += " AND e.Est_Jornada LIKE %s"
            params.append(f"{jornada_sel}%")
        if sede_sel:
            sql += " AND (s.Sed_NomSede LIKE %s OR %s LIKE CONCAT('%%', s.Sed_NomSede, '%%'))"
            params.extend([f"%{sede_sel}%", sede_sel])
        if estado_sel:
            sql += " AND e.Est_Estado = %s"
            params.append(estado_sel)
        if anio_sel:
            sql += " AND e.Est_AnioLectivo = %s"
            params.append(int(anio_sel))

        sql += " ORDER BY e.Est_Apellido ASC, e.Est_Nombre ASC;"
        cursor.execute(sql, tuple(params))
        filas = cursor.fetchall()
        cursor.close()
        conn.close()

        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.writer(output, delimiter=',')
        writer.writerow(['Código', 'Apellidos', 'Nombres', 'Grado', 'Grupo', 'Jornada', 'Sede', 'Año', 'Estado', 'Correo', 'Teléfono'])
        for f in filas:
            writer.writerow([
                f['Est_CodEstudiante'],
                f['Est_Apellido'],
                f['Est_Nombre'],
                f['Est_Cod_Grado'],
                f['Gru_NombreGrupo'] or '',
                f['Est_Jornada'] or 'Mañana',
                f['Sed_NomSede'] or 'Sede Central',
                f['Est_AnioLectivo'] or 2026,
                f['Est_Estado'] or 'Activo',
                f['Est_Correo'] or '',
                f['Est_Telefono'] or ''
            ])

        nombre_archivo = f"estudiantes_asistec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={nombre_archivo}"}
        )
    except Exception as e:
        print(f"[ERROR EXPORTAR ESTUDIANTES]: {e}")
        if conn and conn.is_connected():
            conn.close()
        return f"Error exportando estudiantes: {e}", 500

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor ASISTEC en http://localhost:{puerto}...")
    app.run(host='0.0.0.0', port=puerto, debug=False)
