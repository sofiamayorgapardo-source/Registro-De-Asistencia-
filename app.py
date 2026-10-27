import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

# Aseguramos que pueda importar conexion.py esté donde esté y localice html y css
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_raiz = directorio_actual if os.path.isdir(os.path.join(directorio_actual, "html")) else os.path.dirname(directorio_actual)
sys.path.append(directorio_raiz)
sys.path.append(os.path.join(directorio_raiz, "python"))

from conexion import obtener_conexion

# Flask busca las páginas en html/ y los estilos en css/
app = Flask(
    __name__,
    template_folder=os.path.join(directorio_raiz, "html"),
    static_folder=os.path.join(directorio_raiz, "css"),
    static_url_path="/css"
)

# Clave secreta para el manejo seguro de sesiones
app.secret_key = 'asistec_clave_secreta_2026'


# =========================================================================
# REGLAS ACADÉMICAS INSTITUCIONALES — GRADOS 1 A 11, ASIGNATURAS Y MODALIDADES
# =========================================================================

ASIGNATURAS_GENERALES = [
    'Tecnología',
    'Ciencias Naturales',
    'Inglés',
    'Matemáticas',
    'Lenguaje',
    'Educación',
    'Artística',
    'Religión',
    'Emprendimiento',
    'Ética',
    'Sociales'
]

ASIGNATURAS_TODAS = [
    'Tecnología',
    'Ciencias Naturales',
    'Inglés',
    'Matemáticas',
    'Lenguaje',
    'Educación',
    'Artística',
    'Religión',
    'Emprendimiento',
    'Ética',
    'Sociales',
    'Física',
    'Filosofía',
    'Contabilidad',
    'Economía'
]

MODALIDADES_TECNICAS = [
    'General',
    'Técnico Contable',
    'Técnico en Programación de Software'
]

def normalizar_grado_num(grado):
    """Convierte cualquier representación de grado a entero (0 a 11, donde 0 es Transición)."""
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
# GRUPOS ACADÉMICOS POR GRADO — ASIGNACIÓN ESTRICTA E INSTITUCIONAL
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
    """
    Devuelve la lista de nombres de grupos permitidos para un grado.
    """
    if grado is None:
        return []
    s = str(grado).strip().lower().replace('grado', '').replace('º', '').replace('°', '').strip()
    if 'transici' in s or s == '0':
        return ['Transición']
    return GRUPOS_POR_GRADO.get(s, [])

def grupo_valido_para_grado(grado, grupo_id_o_nombre):
    """
    Valida si un grupo (ID o nombre) corresponde académicamente al grado.
    """
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
    ÚNICA FUENTE DE VERDAD:
    Devuelve la lista de asignaturas académicamente válidas
    según el grado (Transición / 1 a 11) y la modalidad técnica.
    """
    g_num = normalizar_grado_num(grado)
    if g_num is None:
        return list(ASIGNATURAS_TODAS)

    mod = str(modalidad or '').strip().lower()
    es_contable = 'contable' in mod
    es_software = 'software' in mod or 'program' in mod

    # 1. Transición y Grados 1 a 7: Exclusivamente las 11 asignaturas generales
    if g_num <= 7:
        return list(ASIGNATURAS_GENERALES)

    # 2. Grados 8 y 9: Asignaturas generales + Contabilidad
    if g_num in [8, 9]:
        return list(ASIGNATURAS_GENERALES) + ['Contabilidad']

    # 3. Grados 10 y 11:
    if g_num in [10, 11]:
        if es_contable:
            # Técnico Contable: NO Tecnología, SÍ Contabilidad, SÍ Economía, SÍ Física, SÍ Filosofía, SÍ demás generales
            materias = [m for m in ASIGNATURAS_GENERALES if m != 'Tecnología']
            materias.extend(['Física', 'Filosofía', 'Contabilidad', 'Economía'])
            return materias
        elif es_software:
            # Técnico en Programación de Software: SÍ Tecnología, NO Contabilidad, SÍ Economía, SÍ Física, SÍ Filosofía, SÍ demás generales
            materias = list(ASIGNATURAS_GENERALES)
            materias.extend(['Física', 'Filosofía', 'Economía'])
            return materias
        else:
            # Modalidad General / Académica:
            # Generales + Física + Filosofía + Economía (Contabilidad NO si no es Técnico Contable)
            materias = list(ASIGNATURAS_GENERALES)
            materias.extend(['Física', 'Filosofía', 'Economía'])
            return materias

    return list(ASIGNATURAS_GENERALES)

def asignatura_valida(grado, modalidad, asignatura):
    """
    Valida si una combinación (grado, modalidad, asignatura) es académicamente válida.
    """
    if not asignatura:
        return True
    asig_nombre = str(asignatura).strip().lower()
    validas = obtener_asignaturas_validas(grado, modalidad)
    validas_lower = [v.lower() for v in validas]
    
    for v_nom in validas_lower:
        if asig_nombre == v_nom or v_nom in asig_nombre or asig_nombre in v_nom:
            return True
    return False


@app.route('/api/asignaturas_validas')
def api_asignaturas_validas():
    """
    API JSON que devuelve las asignaturas válidas dinámicamente según grado y modalidad.
    """
    grado = request.args.get('grado', '')
    modalidad = request.args.get('modalidad', '')
    materias = obtener_asignaturas_validas(grado, modalidad)
    
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
            for f in filas:
                if f['Asi_NomAsignatura'].lower() == m.lower() or m.lower() in f['Asi_NomAsignatura'].lower():
                    cod = f['Asi_CodAsignatura']
                    break
            items.append({'id': cod or m, 'nombre': m})
    else:
        items = [{'id': m, 'nombre': m} for m in materias]
        
    return jsonify(items)


@app.route('/api/grupos_validos')
def api_grupos_validos():
    """
    API JSON que devuelve los grupos válidos dinámicamente según el grado.
    """
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


@app.route('/')
def inicio():
    """
    Ruta raíz: Redirige automáticamente según el estado de la sesión.
    """
    if 'usuario' in session:
        if session.get('rol') == 'docente':
            return redirect(url_for('panel_docente'))
        elif session.get('rol') == 'coordinador':
            return redirect(url_for('coordinador'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta de autenticación de usuarios con validación de credenciales y roles.
    """
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()

        # Validación de campos vacíos
        if not usuario or not password:
            return render_template('login.html', error="Por favor ingresa tu usuario y contraseña.")
        
        conexion = obtener_conexion()
        if conexion and conexion.is_connected():
            try:
                cursor = conexion.cursor(dictionary=True)
                sql = "SELECT id_usuario, usuario, password, rol, id_docente FROM usuarios WHERE usuario = %s AND password = %s;"
                cursor.execute(sql, (usuario, password))
                usuario_encontrado = cursor.fetchone()
                
                cursor.close()
                conexion.close()
                
                if usuario_encontrado:
                    # Guardamos los datos de identidad en la sesión
                    session['usuario'] = usuario_encontrado['usuario']
                    session['rol'] = usuario_encontrado['rol']
                    session['id_docente'] = usuario_encontrado['id_docente']
                    
                    if usuario_encontrado['rol'] == 'docente':
                        return redirect(url_for('panel_docente'))
                    elif usuario_encontrado['rol'] == 'coordinador':
                        return redirect(url_for('coordinador'))
                    else:
                        session.clear()
                        return render_template('login.html', error="Rol de usuario no autorizado.")
                else:
                    return render_template('login.html', error="Usuario o contraseña incorrectos.")
            except Exception as e:
                print(f"[ERROR BD LOGIN]: {e}")
                return render_template('login.html', error="Ocurrió un error al verificar tus credenciales en el sistema.")
        else:
            return render_template('login.html', error="No fue posible conectar con la base de datos. Verifique que MySQL esté funcionando en XAMPP.")
            
    if 'usuario' in session:
        if session.get('rol') == 'docente':
            return redirect(url_for('panel_docente'))
        elif session.get('rol') == 'coordinador':
            return redirect(url_for('coordinador'))
            
    return render_template('login.html')


@app.route('/panel_docente')
@app.route('/docente_panel')
def panel_docente():
    """
    Panel principal del Docente con los 5 botones de navegación institucional
    y los módulos operativos de asistencia.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if session.get('rol') != 'docente':
        return redirect(url_for('coordinador'))
        
    return render_template('panel_docente.html', usuario=session.get('usuario'), rol='docente')


@app.route('/coordinador')
def coordinador():
    """
    Panel principal del Coordinador con los 5 botones de navegación institucional
    y los módulos de supervisión.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if session.get('rol') != 'coordinador':
        return redirect(url_for('panel_docente'))
        
    return render_template('coordinador.html', usuario=session.get('usuario'), rol='coordinador')


# =========================================================================
# RUTAS DE LOS 5 BOTONES DE NAVEGACIÓN INSTITUCIONAL
# =========================================================================

@app.route('/grupo')
def grupo():
    """
    Botón GRUPO:
    Consulta los grupos registrados en la tabla 'grupo' de MySQL.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        # Consulta de grupos y conteo de estudiantes asignados
        sql_grupos = """
            SELECT 
                g.Gru_Codigo, 
                g.Gru_NombreGrupo, 
                COUNT(e.Est_CodEstudiante) AS total_estudiantes
            FROM grupo g
            LEFT JOIN estudiantes e ON g.Gru_Codigo = e.Est_Cod_Grupo
            GROUP BY g.Gru_Codigo, g.Gru_NombreGrupo
            ORDER BY g.Gru_Codigo;
        """
        cursor.execute(sql_grupos)
        grupos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM estudiantes;")
        total_estudiantes = cursor.fetchone()['total']

        cursor.close()
        conexion.close()

        return render_template(
            'grupo.html',
            grupos=grupos,
            total_estudiantes=total_estudiantes,
            usuario=usuario,
            rol=rol
        )
    except Exception as e:
        print(f"[ERROR GRUPO]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Error al consultar los grupos en la base de datos.")


@app.route('/grado')
def grado():
    """
    Botón GRADO:
    Consulta los grados registrados en la tabla 'grado' de MySQL.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        # Consulta de grados y conteo de estudiantes asignados
        sql_grados = """
            SELECT 
                g.Gra_Codigo, 
                g.Gra_NombreGrado, 
                COUNT(e.Est_CodEstudiante) AS total_estudiantes
            FROM grado g
            LEFT JOIN estudiantes e ON g.Gra_Codigo = e.Est_Cod_Grado
            GROUP BY g.Gra_Codigo, g.Gra_NombreGrado
            ORDER BY g.Gra_Codigo;
        """
        cursor.execute(sql_grados)
        grados = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM estudiantes;")
        total_estudiantes = cursor.fetchone()['total']

        cursor.close()
        conexion.close()

        return render_template(
            'grado.html',
            grados=grados,
            total_estudiantes=total_estudiantes,
            usuario=usuario,
            rol=rol
        )
    except Exception as e:
        print(f"[ERROR GRADO]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Error al consultar los grados en la base de datos.")


@app.route('/jornada')
def jornada():
    """
    Botón JORNADA:
    Consulta la información y distribución de jornadas académicas institucionales
    relacionadas con los horarios de registro de asistencia (Reg_FechaHoraIngreso)
    y la sede institucional en la base de datos.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Sed_NomSede FROM sedes LIMIT 1;")
        res_sede = cursor.fetchone()
        sede_nombre = res_sede['Sed_NomSede'] if res_sede else 'Sede Principal'

        cursor.close()
        conexion.close()

        return render_template(
            'jornada.html',
            sede_nombre=sede_nombre,
            usuario=usuario,
            rol=rol
        )
    except Exception as e:
        print(f"[ERROR JORNADA]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Error al consultar las jornadas.")


@app.route('/docente')
def docente():
    """
    Botón DOCENTE:
    Muestra los docentes registrados en la tabla real 'docentes' de MySQL,
    con su asignatura vinculada y datos de contacto públicos (sin contraseñas).
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        sql_docentes = """
            SELECT 
                d.Doc_CodDocentes,
                d.Doc_Nombres,
                d.Doc_Apellidos,
                d.Doc_Correo,
                d.Doc_Telefono,
                d.Doc_Genero,
                d.Doc_Obcervacion,
                COALESCE(a.Asi_NomAsignatura, 'Tecnología e Informática') AS Asignatura
            FROM docentes d
            LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            ORDER BY d.Doc_CodDocentes;
        """
        cursor.execute(sql_docentes)
        docentes = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template(
            'docente.html',
            docentes=docentes,
            usuario=usuario,
            rol=rol
        )
    except Exception as e:
        print(f"[ERROR DOCENTE]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Error al consultar los docentes en la base de datos.")


@app.route('/asignatura')
def asignatura():
    """
    Botón ASIGNATURA:
    Muestra las asignaturas registradas en la tabla 'asignatura' de MySQL.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos.")

    try:
        cursor = conexion.cursor(dictionary=True)
        sql_asignaturas = """
            SELECT 
                a.Asi_CodAsignatura, 
                a.Asi_NomAsignatura,
                COUNT(d.Doc_CodDocentes) AS total_docentes
            FROM asignatura a
            LEFT JOIN docentes d ON a.Asi_CodAsignatura = d.Doc_Cod_Asignatura
            GROUP BY a.Asi_CodAsignatura, a.Asi_NomAsignatura
            ORDER BY a.Asi_CodAsignatura;
        """
        cursor.execute(sql_asignaturas)
        asignaturas = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template(
            'asignatura.html',
            asignaturas=asignaturas,
            usuario=usuario,
            rol=rol
        )
    except Exception as e:
        print(f"[ERROR ASIGNATURA]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Error al consultar las asignaturas en la base de datos.")


# =========================================================================
# MÓDULOS OPERATIVOS DE ASISTENCIA (DOCENTE Y COORDINADOR)
# =========================================================================

@app.route('/registrar_asistencia', methods=['GET'])
def registrar_asistencia():
    """
    Muestra la interfaz para registrar asistencia (exclusivo para Docente).
    Integra los datos de Grado, Grupo, Jornada, Docente y Asignatura.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if session.get('rol') != 'docente':
        return redirect(url_for('coordinador'))

    id_docente = session.get('id_docente')
    grado_sel = request.args.get('grado', '').strip()
    grupo_sel = request.args.get('grupo', '').strip()
    modalidad_sel = request.args.get('modalidad', 'General').strip()
    jornada_sel = request.args.get('jornada', 'Mañana').strip()
    asignatura_sel = request.args.get('asignatura', '').strip()
    
    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('registrar_asistencia.html', error="No fue posible conectar con la base de datos. Verifique que MySQL esté funcionando en XAMPP.", usuario=session.get('usuario'))

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()
        
        if grado_sel:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_sel,))
            grupos = cursor.fetchall()
        else:
            grupos = []

        cursor.execute("SELECT Asi_CodAsignatura, Asi_NomAsignatura FROM asignatura ORDER BY Asi_CodAsignatura;")
        todas_asignaturas = cursor.fetchall()

        # Determinar el nombre/número del grado seleccionado
        grado_num_actual = grado_sel
        for g in grados:
            if str(g['Gra_Codigo']) == str(grado_sel):
                grado_num_actual = g['Gra_NombreGrado']
                break

        # Filtrar asignaturas académicamente válidas para este grado y modalidad
        asignaturas_validas_nombres = obtener_asignaturas_validas(grado_num_actual, modalidad_sel)
        asignaturas = [a for a in todas_asignaturas if any(a['Asi_NomAsignatura'].lower() == v.lower() for v in asignaturas_validas_nombres)]
        if not asignaturas:
            asignaturas = todas_asignaturas

        # Datos del docente en sesión
        cursor.execute("""
            SELECT d.Doc_CodDocentes, d.Doc_Nombres, d.Doc_Apellidos, d.Doc_Cod_Asignatura, a.Asi_NomAsignatura 
            FROM docentes d 
            LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            WHERE d.Doc_CodDocentes = %s;
        """, (id_docente,))
        docente_actual = cursor.fetchone()

        # Si la asignatura actual del docente no es válida en este grado/modalidad, deseleccionarla
        if docente_actual and docente_actual.get('Asi_NomAsignatura'):
            if not asignatura_valida(grado_num_actual, modalidad_sel, docente_actual['Asi_NomAsignatura']):
                if asignatura_sel == str(docente_actual.get('Doc_Cod_Asignatura')):
                    asignatura_sel = ''
            elif not asignatura_sel and docente_actual.get('Doc_Cod_Asignatura'):
                asignatura_sel = str(docente_actual['Doc_Cod_Asignatura'])

        # Si hay una asignatura seleccionada, verificar que sea válida
        error_validacion = None
        if grado_sel and asignatura_sel:
            nombre_asig_verif = ''
            for a in todas_asignaturas:
                if str(a['Asi_CodAsignatura']) == str(asignatura_sel) or a['Asi_NomAsignatura'] == asignatura_sel:
                    nombre_asig_verif = a['Asi_NomAsignatura']
                    break
            if nombre_asig_verif and not asignatura_valida(grado_num_actual, modalidad_sel, nombre_asig_verif):
                error_validacion = f"La asignatura '{nombre_asig_verif}' no está permitida para Grado {grado_num_actual} (Modalidad: {modalidad_sel})."
                asignatura_sel = ''

        # Validar coherencia grupo y grado
        if grado_sel and grupo_sel:
            cursor.execute("SELECT Gru_NombreGrupo, Gru_Cod_Grado FROM grupo WHERE Gru_Codigo = %s;", (grupo_sel,))
            grp_row = cursor.fetchone()
            if grp_row and str(grp_row.get('Gru_Cod_Grado')) != str(grado_sel):
                error_validacion = f"El grupo '{grp_row.get('Gru_NombreGrupo')}' no corresponde al grado seleccionado."
                grupo_sel = ''

        jornadas = ['Mañana', 'Tarde', 'Única']
        modalidades = MODALIDADES_TECNICAS
        
        estudiantes = None
        if grado_sel and grupo_sel:
            sql_estudiantes = """
                SELECT Est_CodEstudiante, Est_Nombre, Est_Apellido 
                FROM estudiantes 
                WHERE Est_Cod_Grado = %s AND Est_Cod_Grupo = %s 
                ORDER BY Est_Apellido, Est_Nombre;
            """
            cursor.execute(sql_estudiantes, (grado_sel, grupo_sel))
            estudiantes = cursor.fetchall()
            
        cursor.close()
        conexion.close()
        
        return render_template(
            'registrar_asistencia.html',
            grados=grados,
            grupos=grupos,
            asignaturas=asignaturas,
            todas_asignaturas=todas_asignaturas,
            jornadas=jornadas,
            modalidades=modalidades,
            docente_actual=docente_actual,
            grado_seleccionado=grado_sel,
            grupo_seleccionado=grupo_sel,
            modalidad_seleccionada=modalidad_sel,
            jornada_seleccionada=jornada_sel,
            asignatura_seleccionada=asignatura_sel,
            estudiantes=estudiantes,
            error=error_validacion,
            usuario=session.get('usuario')
        )
    except Exception as e:
        print(f"[ERROR REGISTRAR ASISTENCIA]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('registrar_asistencia.html', error="Ocurrió un error al cargar la información de los estudiantes.", usuario=session.get('usuario'))


@app.route('/guardar_asistencia', methods=['POST'])
def guardar_asistencia():
    """
    Procesa y guarda los registros de asistencia en MySQL con validaciones estrictas.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if session.get('rol') != 'docente':
        return redirect(url_for('coordinador'))

    id_docente = session.get('id_docente')
    if not id_docente:
        return render_template('registrar_asistencia.html', error="Error de seguridad: No hay un docente asociado a esta sesión.", usuario=session.get('usuario'))

    grado_id = request.form.get('grado_id', '').strip()
    grupo_id = request.form.get('grupo_id', '').strip()
    modalidad_id = request.form.get('modalidad_id', 'General').strip()
    jornada_id = request.form.get('jornada_id', 'Mañana').strip()
    asignatura_id = request.form.get('asignatura_id', '').strip()
    if not grado_id or not grupo_id:
        return render_template('registrar_asistencia.html', error="Debes seleccionar un grado y un grupo válidos.", usuario=session.get('usuario'))

    estudiantes_ids = request.form.getlist('estudiantes_ids')
    if not estudiantes_ids:
        return render_template('registrar_asistencia.html', error="No hay estudiantes seleccionados para registrar asistencia.", usuario=session.get('usuario'))

    estados_validos = {'Presente', 'Ausente', 'Tarde'}
    asistencias_a_guardar = []
    for est_id in estudiantes_ids:
        estado = request.form.get(f'estado_{est_id}', '').strip()
        if estado not in estados_validos:
            return render_template('registrar_asistencia.html', error=f"El estado seleccionado para el estudiante {est_id} no es válido.", usuario=session.get('usuario'))
        asistencias_a_guardar.append((est_id, estado))

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('registrar_asistencia.html', error="No fue posible conectar con la base de datos. Verifique que MySQL esté funcionando en XAMPP.", usuario=session.get('usuario'))

    try:
        cursor = conexion.cursor(dictionary=True)

        # Consultar nombres de grado y asignatura para validación institucional
        cursor.execute("SELECT Gra_NombreGrado FROM grado WHERE Gra_Codigo = %s;", (grado_id,))
        res_g = cursor.fetchone()
        grado_nom = res_g['Gra_NombreGrado'] if res_g else grado_id

        asig_nom = ''
        if asignatura_id:
            cursor.execute("SELECT Asi_NomAsignatura FROM asignatura WHERE Asi_CodAsignatura = %s;", (asignatura_id,))
            res_a = cursor.fetchone()
            asig_nom = res_a['Asi_NomAsignatura'] if res_a else asignatura_id

        # VALIDACIÓN OBLIGATORIA DEL LADO DEL SERVIDOR (ASIGNATURA)
        if asig_nom and not asignatura_valida(grado_nom, modalidad_id, asig_nom):
            cursor.close()
            conexion.close()
            return render_template(
                'registrar_asistencia.html',
                error=f"Rechazado por regla académica: La asignatura '{asig_nom}' no está permitida para Grado {grado_nom} (Modalidad: {modalidad_id}).",
                usuario=session.get('usuario')
            )

        # VALIDACIÓN OBLIGATORIA DEL LADO DEL SERVIDOR (GRUPO)
        cursor.execute("SELECT Gru_NombreGrupo, Gru_Cod_Grado FROM grupo WHERE Gru_Codigo = %s;", (grupo_id,))
        res_grp = cursor.fetchone()
        if res_grp and str(res_grp.get('Gru_Cod_Grado')) != str(grado_id):
            cursor.close()
            conexion.close()
            return render_template(
                'registrar_asistencia.html',
                error=f"Rechazado por regla académica: El grupo '{res_grp.get('Gru_NombreGrupo')}' no corresponde al Grado {grado_nom}.",
                usuario=session.get('usuario')
            )
        
        ahora = datetime.now()
        fecha_solo = ahora.strftime("%Y-%m-%d")
        
        # Ajuste inteligente de la hora para mantener congruencia con la jornada seleccionada
        if jornada_id == 'Tarde':
            if ahora.hour < 13 or ahora.hour >= 19:
                hora_solo = f"14:{ahora.strftime('%M:%S')}"
            else:
                hora_solo = ahora.strftime("%H:%M:%S")
        else: # Mañana / Única
            if ahora.hour < 6 or ahora.hour >= 13:
                hora_solo = f"08:{ahora.strftime('%M:%S')}"
            else:
                hora_solo = ahora.strftime("%H:%M:%S")

        fecha_hora_texto = f"{fecha_solo} {hora_solo}"

        # Si el docente seleccionó una asignatura específica, asociamos su asignatura oficial
        if asignatura_id:
            cursor.execute("UPDATE docentes SET Doc_Cod_Asignatura = %s WHERE Doc_CodDocentes = %s;", (asignatura_id, id_docente))

        # Validación Anti-duplicados por doble clic rápido en los últimos 10 segundos
        primer_estudiante = estudiantes_ids[0]
        cursor.execute("""
            SELECT Reg_FechaHoraIngreso FROM registroasistencia 
            WHERE Reg_CodDocente = %s AND Reg_CodEstudiante = %s 
            ORDER BY Reg_CodRegistroAsistencia DESC LIMIT 1;
        """, (id_docente, primer_estudiante))
        ultimo_registro = cursor.fetchone()
        
        if ultimo_registro and ultimo_registro['Reg_FechaHoraIngreso'].startswith(fecha_solo):
            try:
                ultimo_tiempo = datetime.strptime(ultimo_registro['Reg_FechaHoraIngreso'], "%Y-%m-%d %H:%M:%S")
                if (ahora - ultimo_tiempo).total_seconds() < 10:
                    cursor.close()
                    conexion.close()
                    return render_template('registrar_asistencia.html', error="Aviso: La asistencia de este grupo ya se guardó hace unos segundos (evitando duplicado).", usuario=session.get('usuario'))
            except Exception:
                pass

        sql_insert = """
            INSERT INTO registroasistencia (Reg_CodEstudiante, Reg_CodDocente, Reg_FechaHoraIngreso, Reg_Observacion)
            VALUES (%s, %s, %s, %s);
        """
        for est_id, estado in asistencias_a_guardar:
            cursor.execute(sql_insert, (est_id, id_docente, fecha_hora_texto, estado))

        conexion.commit()

        cursor.execute("SELECT Gru_NombreGrupo FROM grupo WHERE Gru_Codigo = %s;", (grupo_id,))
        res_gr = cursor.fetchone()
        grupo_nom = res_gr['Gru_NombreGrupo'] if res_gr else grupo_id

        confirmacion = {
            'docente': session.get('usuario'),
            'grado': grado_nom,
            'grupo': grupo_nom,
            'modalidad': modalidad_id,
            'jornada': jornada_id,
            'asignatura': asig_nom if asig_nom else 'Tecnología',
            'fecha': fecha_solo,
            'hora': hora_solo,
            'total': len(asistencias_a_guardar)
        }

        cursor.close()
        conexion.close()

        return render_template('registrar_asistencia.html', confirmacion=confirmacion, usuario=session.get('usuario'))

    except Exception as e:
        print(f"[ERROR GUARDAR ASISTENCIA]: {e}")
        if conexion and conexion.is_connected():
            conexion.rollback()
            conexion.close()
        return render_template('registrar_asistencia.html', error="Ocurrió un error al guardar los registros en la base de datos.", usuario=session.get('usuario'))


@app.route('/consultar_asistencia')
def consultar_asistencia():
    """
    Permite consultar los registros de asistencia con filtros por fecha, grado, grupo,
    jornada, docente, asignatura y estado.
    - Docente: Consulta sus registros propios o según permisos.
    - Coordinador: Consulta registros generales de toda la institución.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')
    id_docente = session.get('id_docente')

    fecha_filtro = request.args.get('fecha', '').strip()
    grado_filtro = request.args.get('grado', '').strip()
    grupo_filtro = request.args.get('grupo', '').strip()
    modalidad_filtro = request.args.get('modalidad', 'General').strip()
    jornada_filtro = request.args.get('jornada', '').strip()
    docente_filtro = request.args.get('docente', '').strip()
    asignatura_filtro = request.args.get('asignatura', '').strip()
    estado_filtro = request.args.get('estado', '').strip()

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos. Verifique que MySQL esté funcionando en XAMPP.")

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        if grado_filtro:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_filtro,))
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
        grupos = cursor.fetchall()

        cursor.execute("SELECT Doc_CodDocentes, Doc_Nombres, Doc_Apellidos FROM docentes ORDER BY Doc_Apellidos, Doc_Nombres;")
        docentes = cursor.fetchall()

        cursor.execute("SELECT Asi_CodAsignatura, Asi_NomAsignatura FROM asignatura ORDER BY Asi_CodAsignatura;")
        asignaturas = cursor.fetchall()

        jornadas = ['Mañana', 'Tarde', 'Única']

        # Obtener nombres para validación académica
        grado_nom_filtro = ''
        if grado_filtro:
            for g in grados:
                if str(g['Gra_Codigo']) == str(grado_filtro):
                    grado_nom_filtro = g['Gra_NombreGrado']
                    break
            if not grado_nom_filtro:
                grado_nom_filtro = grado_filtro

        nombre_asig_filtro = ''
        if asignatura_filtro:
            for a in asignaturas:
                if str(a['Asi_CodAsignatura']) == str(asignatura_filtro) or a['Asi_NomAsignatura'] == asignatura_filtro:
                    nombre_asig_filtro = a['Asi_NomAsignatura']
                    break

        # VALIDACIÓN ACADÉMICA ESTRICTA: Coherencia Grado y Grupo
        if grado_filtro and grupo_filtro:
            cursor.execute("SELECT Gru_NombreGrupo, Gru_Cod_Grado FROM grupo WHERE Gru_Codigo = %s;", (grupo_filtro,))
            res_grp_c = cursor.fetchone()
            if res_grp_c and str(res_grp_c.get('Gru_Cod_Grado')) != str(grado_filtro):
                cursor.close()
                conexion.close()
                filtros = {
                    'fecha': fecha_filtro,
                    'grado': grado_filtro,
                    'grupo': grupo_filtro,
                    'modalidad': modalidad_filtro,
                    'jornada': jornada_filtro,
                    'docente': docente_filtro,
                    'asignatura': asignatura_filtro,
                    'estado': estado_filtro
                }
                return render_template(
                    'consultar_asistencia.html',
                    grados=grados,
                    grupos=grupos,
                    docentes=docentes,
                    asignaturas=asignaturas,
                    jornadas=jornadas,
                    modalidades=MODALIDADES_TECNICAS,
                    registros=[],
                    resumen={'total': 0, 'presentes': 0, 'ausentes': 0, 'tardes': 0},
                    filtros=filtros,
                    error=f"El grupo '{res_grp_c.get('Gru_NombreGrupo')}' no corresponde a Grado {grado_nom_filtro}.",
                    rol=rol,
                    usuario=usuario
                )

        # VALIDACIÓN ACADÉMICA ESTRICTA: Rechazar consultas académicamente inválidas
        if grado_filtro and asignatura_filtro and nombre_asig_filtro:
            if not asignatura_valida(grado_nom_filtro, modalidad_filtro, nombre_asig_filtro):
                cursor.close()
                conexion.close()
                filtros = {
                    'fecha': fecha_filtro,
                    'grado': grado_filtro,
                    'grupo': grupo_filtro,
                    'modalidad': modalidad_filtro,
                    'jornada': jornada_filtro,
                    'docente': docente_filtro,
                    'asignatura': asignatura_filtro,
                    'estado': estado_filtro
                }
                return render_template(
                    'consultar_asistencia.html',
                    grados=grados,
                    grupos=grupos,
                    docentes=docentes,
                    asignaturas=asignaturas,
                    jornadas=jornadas,
                    modalidades=MODALIDADES_TECNICAS,
                    registros=[],
                    resumen={'total': 0, 'presentes': 0, 'ausentes': 0, 'tardes': 0},
                    filtros=filtros,
                    error_validacion=f"Consulta inválida: La asignatura '{nombre_asig_filtro}' no se imparte en Grado {grado_nom_filtro} (Modalidad: {modalidad_filtro}).",
                    rol=rol,
                    usuario=usuario
                )

        sql = """
            SELECT 
                r.Reg_CodRegistroAsistencia,
                r.Reg_FechaHoraIngreso,
                r.Reg_Observacion AS Estado,
                e.Est_CodEstudiante,
                e.Est_Nombre,
                e.Est_Apellido,
                g.Gra_NombreGrado,
                gr.Gru_NombreGrupo,
                d.Doc_CodDocentes,
                d.Doc_Nombres,
                d.Doc_Apellidos,
                COALESCE(a.Asi_NomAsignatura, 'Tecnología e Informática') AS Asi_NomAsignatura,
                CASE 
                    WHEN TIME(r.Reg_FechaHoraIngreso) BETWEEN '13:00:00' AND '18:59:59' THEN 'Tarde'
                    ELSE 'Mañana'
                END AS Jornada
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
        elif docente_filtro:
            condiciones.append("r.Reg_CodDocente = %s")
            parametros.append(docente_filtro)

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
            condiciones.append("(d.Doc_Cod_Asignatura = %s OR a.Asi_CodAsignatura = %s)")
            parametros.extend([asignatura_filtro, asignatura_filtro])

        if jornada_filtro == 'Mañana':
            condiciones.append("(TIME(r.Reg_FechaHoraIngreso) BETWEEN '06:00:00' AND '12:59:59' OR r.Reg_FechaHoraIngreso LIKE '%08:00:00%')")
        elif jornada_filtro == 'Tarde':
            condiciones.append("TIME(r.Reg_FechaHoraIngreso) BETWEEN '13:00:00' AND '18:59:59'")

        if estado_filtro in ['Presente', 'Ausente', 'Tarde']:
            condiciones.append("r.Reg_Observacion = %s")
            parametros.append(estado_filtro)

        if condiciones:
            sql += " AND " + " AND ".join(condiciones)

        sql += " ORDER BY r.Reg_FechaHoraIngreso DESC, e.Est_Apellido ASC, e.Est_Nombre ASC;"

        cursor.execute(sql, tuple(parametros))
        filas = cursor.fetchall()

        cursor.close()
        conexion.close()

        registros = []
        for fila in filas:
            fecha_hora = str(fila['Reg_FechaHoraIngreso'])
            partes = fecha_hora.split(' ')
            fecha_str = partes[0] if len(partes) > 0 else fecha_hora
            hora_str = partes[1] if len(partes) > 1 else ''

            registros.append({
                'Reg_CodRegistroAsistencia': fila['Reg_CodRegistroAsistencia'],
                'Fecha': fecha_str,
                'Hora': hora_str,
                'Est_CodEstudiante': fila['Est_CodEstudiante'],
                'Est_Nombre': fila['Est_Nombre'],
                'Est_Apellido': fila['Est_Apellido'],
                'Gra_NombreGrado': fila['Gra_NombreGrado'],
                'Gru_NombreGrupo': fila['Gru_NombreGrupo'],
                'Doc_Nombres': fila['Doc_Nombres'] if fila['Doc_Nombres'] else 'Docente',
                'Doc_Apellidos': fila['Doc_Apellidos'] if fila['Doc_Apellidos'] else '',
                'Asignatura': fila['Asi_NomAsignatura'],
                'Jornada': fila['Jornada'],
                'Estado': fila['Estado']
            })

        resumen = {
            'total': len(registros),
            'presentes': sum(1 for r in registros if r['Estado'] == 'Presente'),
            'ausentes': sum(1 for r in registros if r['Estado'] == 'Ausente'),
            'tardes': sum(1 for r in registros if r['Estado'] == 'Tarde')
        }

        filtros = {
            'fecha': fecha_filtro,
            'grado': grado_filtro,
            'grupo': grupo_filtro,
            'modalidad': modalidad_filtro,
            'jornada': jornada_filtro,
            'docente': docente_filtro,
            'asignatura': asignatura_filtro,
            'estado': estado_filtro
        }

        return render_template(
            'consultar_asistencia.html',
            grados=grados,
            grupos=grupos,
            docentes=docentes,
            asignaturas=asignaturas,
            jornadas=jornadas,
            modalidades=MODALIDADES_TECNICAS,
            registros=registros,
            resumen=resumen,
            filtros=filtros,
            rol=rol,
            usuario=usuario
        )

    except Exception as e:
        print(f"[ERROR CONSULTAR ASISTENCIA]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Ocurrió un problema al consultar la información de asistencia.")


@app.route('/reporte')
def reporte():
    """
    Genera el reporte de asistencia ordenado para consultar e imprimir desde Google Chrome.
    Integra filtros de Grado, Grupo, Jornada, Docente, Asignatura, Fecha y Estado.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')
    id_docente = session.get('id_docente')

    fecha_filtro = request.args.get('fecha', '').strip()
    grado_filtro = request.args.get('grado', '').strip()
    grupo_filtro = request.args.get('grupo', '').strip()
    modalidad_filtro = request.args.get('modalidad', 'General').strip()
    jornada_filtro = request.args.get('jornada', '').strip()
    docente_filtro = request.args.get('docente', '').strip()
    asignatura_filtro = request.args.get('asignatura', '').strip()
    estado_filtro = request.args.get('estado', '').strip()

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos. Verifique que MySQL esté funcionando en XAMPP.")

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        if grado_filtro:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_filtro,))
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
        grupos = cursor.fetchall()

        cursor.execute("SELECT Doc_CodDocentes, Doc_Nombres, Doc_Apellidos FROM docentes ORDER BY Doc_Apellidos, Doc_Nombres;")
        docentes = cursor.fetchall()

        cursor.execute("SELECT Asi_CodAsignatura, Asi_NomAsignatura FROM asignatura ORDER BY Asi_CodAsignatura;")
        asignaturas = cursor.fetchall()

        jornadas = ['Mañana', 'Tarde', 'Única']

        grado_nom_filtro = ''
        if grado_filtro:
            for g in grados:
                if str(g['Gra_Codigo']) == str(grado_filtro):
                    grado_nom_filtro = g['Gra_NombreGrado']
                    break
            if not grado_nom_filtro:
                grado_nom_filtro = grado_filtro

        nombre_asig_filtro = ''
        if asignatura_filtro:
            for a in asignaturas:
                if str(a['Asi_CodAsignatura']) == str(asignatura_filtro) or a['Asi_NomAsignatura'] == asignatura_filtro:
                    nombre_asig_filtro = a['Asi_NomAsignatura']
                    break

        # VALIDACIÓN ACADÉMICA ESTRICTA: Coherencia Grado y Grupo
        if grado_filtro and grupo_filtro:
            cursor.execute("SELECT Gru_NombreGrupo, Gru_Cod_Grado FROM grupo WHERE Gru_Codigo = %s;", (grupo_filtro,))
            res_grp_rep = cursor.fetchone()
            if res_grp_rep and str(res_grp_rep.get('Gru_Cod_Grado')) != str(grado_filtro):
                cursor.close()
                conexion.close()
                filtros = {
                    'fecha': fecha_filtro,
                    'grado': grado_filtro,
                    'grupo': grupo_filtro,
                    'modalidad': modalidad_filtro,
                    'jornada': jornada_filtro,
                    'docente': docente_filtro,
                    'asignatura': asignatura_filtro,
                    'estado': estado_filtro
                }
                return render_template(
                    'reporte.html',
                    grados=grados,
                    grupos=grupos,
                    docentes=docentes,
                    asignaturas=asignaturas,
                    jornadas=jornadas,
                    modalidades=MODALIDADES_TECNICAS,
                    registros=[],
                    total_registros=0,
                    resumen={'total': 0, 'presentes': 0, 'ausentes': 0, 'tardes': 0},
                    filtros=filtros,
                    grado_nombre_sel=grado_nom_filtro,
                    grupo_nombre_sel=res_grp_rep.get('Gru_NombreGrupo', ''),
                    docente_nombre_sel='',
                    asignatura_nombre_sel='',
                    modalidad_sel=modalidad_filtro,
                    jornada_sel=jornada_filtro,
                    fecha_emision=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    error=f"El grupo '{res_grp_rep.get('Gru_NombreGrupo')}' no corresponde a Grado {grado_nom_filtro}.",
                    rol=rol,
                    usuario=usuario
                )

        # VALIDACIÓN ACADÉMICA ESTRICTA EN REPORTE
        if grado_filtro and asignatura_filtro and nombre_asig_filtro:
            if not asignatura_valida(grado_nom_filtro, modalidad_filtro, nombre_asig_filtro):
                cursor.close()
                conexion.close()
                filtros = {
                    'fecha': fecha_filtro,
                    'grado': grado_filtro,
                    'grupo': grupo_filtro,
                    'modalidad': modalidad_filtro,
                    'jornada': jornada_filtro,
                    'docente': docente_filtro,
                    'asignatura': asignatura_filtro,
                    'estado': estado_filtro
                }
                return render_template(
                    'reporte.html',
                    grados=grados,
                    grupos=grupos,
                    docentes=docentes,
                    asignaturas=asignaturas,
                    jornadas=jornadas,
                    modalidades=MODALIDADES_TECNICAS,
                    registros=[],
                    resumen={'total': 0, 'presentes': 0, 'ausentes': 0, 'tardes': 0},
                    filtros=filtros,
                    grado_nombre_sel=grado_nom_filtro,
                    grupo_nombre_sel='',
                    docente_nombre_sel='',
                    asignatura_nombre_sel=nombre_asig_filtro,
                    modalidad_sel=modalidad_filtro,
                    jornada_sel=jornada_filtro,
                    fecha_emision=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    error_validacion=f"Reporte no disponible: La asignatura '{nombre_asig_filtro}' no es válida para Grado {grado_nom_filtro} (Modalidad: {modalidad_filtro}).",
                    rol=rol,
                    usuario=usuario
                )

        sql = """
            SELECT 
                r.Reg_CodRegistroAsistencia,
                r.Reg_FechaHoraIngreso,
                r.Reg_Observacion AS Estado,
                e.Est_CodEstudiante,
                e.Est_Nombre,
                e.Est_Apellido,
                g.Gra_NombreGrado,
                gr.Gru_NombreGrupo,
                d.Doc_Nombres,
                d.Doc_Apellidos,
                COALESCE(a.Asi_NomAsignatura, 'Tecnología e Informática') AS Asi_NomAsignatura,
                CASE 
                    WHEN TIME(r.Reg_FechaHoraIngreso) BETWEEN '13:00:00' AND '18:59:59' THEN 'Tarde'
                    ELSE 'Mañana'
                END AS Jornada
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
        elif docente_filtro:
            condiciones.append("r.Reg_CodDocente = %s")
            parametros.append(docente_filtro)

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
            condiciones.append("(d.Doc_Cod_Asignatura = %s OR a.Asi_CodAsignatura = %s)")
            parametros.extend([asignatura_filtro, asignatura_filtro])

        if jornada_filtro == 'Mañana':
            condiciones.append("(TIME(r.Reg_FechaHoraIngreso) BETWEEN '06:00:00' AND '12:59:59' OR r.Reg_FechaHoraIngreso LIKE '%08:00:00%')")
        elif jornada_filtro == 'Tarde':
            condiciones.append("TIME(r.Reg_FechaHoraIngreso) BETWEEN '13:00:00' AND '18:59:59'")

        if estado_filtro in ['Presente', 'Ausente', 'Tarde']:
            condiciones.append("r.Reg_Observacion = %s")
            parametros.append(estado_filtro)

        if condiciones:
            sql += " AND " + " AND ".join(condiciones)

        sql += " ORDER BY r.Reg_FechaHoraIngreso DESC, e.Est_Apellido ASC, e.Est_Nombre ASC;"

        cursor.execute(sql, tuple(parametros))
        filas = cursor.fetchall()

        cursor.close()
        conexion.close()

        registros = []
        for fila in filas:
            fecha_hora = str(fila['Reg_FechaHoraIngreso'])
            registros.append({
                'Est_CodEstudiante': fila['Est_CodEstudiante'],
                'Est_Nombre': fila['Est_Nombre'],
                'Est_Apellido': fila['Est_Apellido'],
                'Gra_NombreGrado': fila['Gra_NombreGrado'],
                'Gru_NombreGrupo': fila['Gru_NombreGrupo'],
                'Doc_Nombres': fila['Doc_Nombres'] if fila['Doc_Nombres'] else 'Docente',
                'Doc_Apellidos': fila['Doc_Apellidos'] if fila['Doc_Apellidos'] else '',
                'Asignatura': fila['Asi_NomAsignatura'],
                'Jornada': fila['Jornada'],
                'Estado': fila['Estado'],
                'Reg_FechaHoraIngreso': fecha_hora
            })

        resumen = {
            'total': len(registros),
            'presentes': sum(1 for r in registros if r['Estado'] == 'Presente'),
            'ausentes': sum(1 for r in registros if r['Estado'] == 'Ausente'),
            'tardes': sum(1 for r in registros if r['Estado'] == 'Tarde')
        }

        filtros = {
            'fecha': fecha_filtro,
            'grado': grado_filtro,
            'grupo': grupo_filtro,
            'modalidad': modalidad_filtro,
            'jornada': jornada_filtro,
            'docente': docente_filtro,
            'asignatura': asignatura_filtro,
            'estado': estado_filtro
        }

        grado_nombre_sel = ''
        for g in grados:
            if str(g['Gra_Codigo']) == grado_filtro:
                grado_nombre_sel = g['Gra_NombreGrado']
                break

        grupo_nombre_sel = ''
        for gr in grupos:
            if str(gr['Gru_Codigo']) == grupo_filtro:
                grupo_nombre_sel = gr['Gru_NombreGrupo']
                break

        docente_nombre_sel = ''
        for d in docentes:
            if str(d['Doc_CodDocentes']) == docente_filtro:
                docente_nombre_sel = f"{d['Doc_Nombres']} {d['Doc_Apellidos']}"
                break

        asignatura_nombre_sel = ''
        for a in asignaturas:
            if str(a['Asi_CodAsignatura']) == asignatura_filtro:
                asignatura_nombre_sel = a['Asi_NomAsignatura']
                break

        fecha_emision = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return render_template(
            'reporte.html',
            grados=grados,
            grupos=grupos,
            docentes=docentes,
            asignaturas=asignaturas,
            jornadas=jornadas,
            modalidades=MODALIDADES_TECNICAS,
            registros=registros,
            resumen=resumen,
            filtros=filtros,
            grado_nombre_sel=grado_nombre_sel,
            grupo_nombre_sel=grupo_nombre_sel,
            docente_nombre_sel=docente_nombre_sel,
            asignatura_nombre_sel=asignatura_nombre_sel,
            modalidad_sel=modalidad_filtro,
            jornada_sel=jornada_filtro,
            fecha_emision=fecha_emision,
            rol=rol,
            usuario=usuario
        )

    except Exception as e:
        print(f"[ERROR GENERAR REPORTE]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Ocurrió un problema al generar el reporte de asistencia.")


@app.route('/estadisticas')
def estadisticas():
    """
    Módulo de Estadísticas y Resumen de Asistencia:
    Integra criterios de análisis: Grado, Grupo, Jornada, Docente, Asignatura y Fecha.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session.get('usuario')
    rol = session.get('rol')
    id_docente = session.get('id_docente')

    fecha_filtro = request.args.get('fecha', '').strip()
    grado_filtro = request.args.get('grado', '').strip()
    grupo_filtro = request.args.get('grupo', '').strip()
    jornada_filtro = request.args.get('jornada', '').strip()
    docente_filtro = request.args.get('docente', '').strip()
    asignatura_filtro = request.args.get('asignatura', '').strip()
    modalidad_filtro = request.args.get('modalidad', 'General').strip()

    conexion = obtener_conexion()
    if not conexion or not conexion.is_connected():
        return render_template('login.html', error="No fue posible conectar con la base de datos. Verifique que MySQL esté funcionando en XAMPP.")

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT Gra_Codigo, Gra_NombreGrado FROM grado ORDER BY Gra_Codigo;")
        grados = cursor.fetchall()

        if grado_filtro:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo WHERE Gru_Cod_Grado = %s ORDER BY Gru_Codigo;", (grado_filtro,))
        else:
            cursor.execute("SELECT Gru_Codigo, Gru_NombreGrupo FROM grupo ORDER BY Gru_Codigo;")
        grupos = cursor.fetchall()

        cursor.execute("SELECT Doc_CodDocentes, Doc_Nombres, Doc_Apellidos FROM docentes ORDER BY Doc_Apellidos, Doc_Nombres;")
        docentes = cursor.fetchall()

        cursor.execute("SELECT Asi_CodAsignatura, Asi_NomAsignatura FROM asignatura ORDER BY Asi_CodAsignatura;")
        asignaturas = cursor.fetchall()

        jornadas = ['Mañana', 'Tarde', 'Única']

        # Validación académica de coherencia Grado y Grupo
        if grado_filtro and grupo_filtro:
            cursor.execute("SELECT Gru_NombreGrupo, Gru_Cod_Grado FROM grupo WHERE Gru_Codigo = %s;", (grupo_filtro,))
            res_grp_est = cursor.fetchone()
            if res_grp_est and str(res_grp_est.get('Gru_Cod_Grado')) != str(grado_filtro):
                cursor.close()
                conexion.close()
                filtros_err = {
                    'fecha': fecha_filtro,
                    'grado': grado_filtro,
                    'grupo': grupo_filtro,
                    'jornada': jornada_filtro,
                    'docente': docente_filtro,
                    'asignatura': asignatura_filtro,
                    'modalidad': modalidad_filtro
                }
                grado_nom = next((str(g['Gra_NombreGrado']) for g in grados if str(g['Gra_Codigo']) == str(grado_filtro)), str(grado_filtro))
                return render_template(
                    'estadisticas.html',
                    totales={'total': 0, 'presentes': 0, 'ausentes': 0, 'tardes': 0},
                    porcentajes={'presentes': 0.0, 'ausentes': 0.0, 'tardes': 0.0},
                    estadisticas_grado=[],
                    estadisticas_grupo=[],
                    estadisticas_asignatura=[],
                    estadisticas_jornada=[],
                    estadisticas_docente=[],
                    filtros=filtros_err,
                    grados=grados,
                    grupos=grupos,
                    docentes=docentes,
                    asignaturas=asignaturas,
                    jornadas=jornadas,
                    modalidades=MODALIDADES_TECNICAS,
                    error=f"El grupo '{res_grp_est.get('Gru_NombreGrupo')}' no corresponde a Grado {grado_nom}.",
                    fecha_filtro=fecha_filtro,
                    rol=rol,
                    usuario=usuario
                )

        # Validación académica estricta para grado + asignatura + modalidad
        if grado_filtro and asignatura_filtro:
            grado_nom = next((str(g['Gra_NombreGrado']) for g in grados if str(g['Gra_Codigo']) == str(grado_filtro)), str(grado_filtro))
            asig_nom = next((a['Asi_NomAsignatura'] for a in asignaturas if str(a['Asi_CodAsignatura']) == str(asignatura_filtro)), '')
            if asig_nom and not asignatura_valida(grado_nom, modalidad_filtro, asig_nom):
                cursor.close()
                conexion.close()
                filtros_err = {
                    'fecha': fecha_filtro,
                    'grado': grado_filtro,
                    'grupo': grupo_filtro,
                    'jornada': jornada_filtro,
                    'docente': docente_filtro,
                    'asignatura': asignatura_filtro,
                    'modalidad': modalidad_filtro
                }
                return render_template(
                    'estadisticas.html',
                    totales={'total': 0, 'presentes': 0, 'ausentes': 0, 'tardes': 0},
                    porcentajes={'presentes': 0.0, 'ausentes': 0.0, 'tardes': 0.0},
                    estadisticas_grado=[],
                    estadisticas_grupo=[],
                    estadisticas_asignatura=[],
                    estadisticas_jornada=[],
                    estadisticas_docente=[],
                    filtros=filtros_err,
                    grados=grados,
                    grupos=grupos,
                    docentes=docentes,
                    asignaturas=asignaturas,
                    jornadas=jornadas,
                    modalidades=MODALIDADES_TECNICAS,
                    error=f"La asignatura seleccionada ('{asig_nom}') no está disponible para Grado {grado_nom} ({modalidad_filtro}).",
                    fecha_filtro=fecha_filtro,
                    rol=rol,
                    usuario=usuario
                )

        # 1. Consulta de Totales Generales con filtros integrados
        sql_totales = """
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN r.Reg_Observacion = 'Presente' THEN 1 ELSE 0 END) AS presentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Ausente' THEN 1 ELSE 0 END) AS ausentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Tarde' THEN 1 ELSE 0 END) AS tardes
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
        elif docente_filtro:
            condiciones.append("r.Reg_CodDocente = %s")
            parametros.append(docente_filtro)

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
            condiciones.append("(d.Doc_Cod_Asignatura = %s OR a.Asi_CodAsignatura = %s)")
            parametros.extend([asignatura_filtro, asignatura_filtro])

        if jornada_filtro == 'Mañana':
            condiciones.append("(TIME(r.Reg_FechaHoraIngreso) BETWEEN '06:00:00' AND '12:59:59' OR r.Reg_FechaHoraIngreso LIKE '%08:00:00%')")
        elif jornada_filtro == 'Tarde':
            condiciones.append("TIME(r.Reg_FechaHoraIngreso) BETWEEN '13:00:00' AND '18:59:59'")

        if condiciones:
            sql_totales += " AND " + " AND ".join(condiciones)

        cursor.execute(sql_totales, tuple(parametros))
        res_totales = cursor.fetchone()

        total = int(res_totales['total'] or 0) if res_totales else 0
        presentes = int(res_totales['presentes'] or 0) if res_totales else 0
        ausentes = int(res_totales['ausentes'] or 0) if res_totales else 0
        tardes = int(res_totales['tardes'] or 0) if res_totales else 0

        # Cálculo seguro de porcentajes
        if total > 0:
            porc_presentes = round((presentes / total) * 100, 1)
            porc_ausentes = round((ausentes / total) * 100, 1)
            porc_tardes = round((tardes / total) * 100, 1)
        else:
            porc_presentes = 0.0
            porc_ausentes = 0.0
            porc_tardes = 0.0

        totales = {
            'total': total,
            'presentes': presentes,
            'ausentes': ausentes,
            'tardes': tardes
        }
        porcentajes = {
            'presentes': porc_presentes,
            'ausentes': porc_ausentes,
            'tardes': porc_tardes
        }

        # 2. Resumen por Grado
        sql_grado = """
            SELECT 
                g.Gra_NombreGrado AS grado,
                COUNT(*) AS total,
                SUM(CASE WHEN r.Reg_Observacion = 'Presente' THEN 1 ELSE 0 END) AS presentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Ausente' THEN 1 ELSE 0 END) AS ausentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Tarde' THEN 1 ELSE 0 END) AS tardes
            FROM registroasistencia r
            INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
            INNER JOIN grado g ON e.Est_Cod_Grado = g.Gra_Codigo
            LEFT JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
            LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            WHERE 1=1
        """
        if condiciones:
            sql_grado += " AND " + " AND ".join(condiciones)
        sql_grado += " GROUP BY g.Gra_Codigo, g.Gra_NombreGrado ORDER BY g.Gra_Codigo;"

        cursor.execute(sql_grado, tuple(parametros))
        estadisticas_grado = cursor.fetchall()

        # 3. Resumen por Grupo
        sql_grupo = """
            SELECT 
                gr.Gru_NombreGrupo AS grupo,
                COUNT(*) AS total,
                SUM(CASE WHEN r.Reg_Observacion = 'Presente' THEN 1 ELSE 0 END) AS presentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Ausente' THEN 1 ELSE 0 END) AS ausentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Tarde' THEN 1 ELSE 0 END) AS tardes
            FROM registroasistencia r
            INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
            INNER JOIN grupo gr ON e.Est_Cod_Grupo = gr.Gru_Codigo
            LEFT JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
            LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            WHERE 1=1
        """
        if condiciones:
            sql_grupo += " AND " + " AND ".join(condiciones)
        sql_grupo += " GROUP BY gr.Gru_Codigo, gr.Gru_NombreGrupo ORDER BY gr.Gru_Codigo;"

        cursor.execute(sql_grupo, tuple(parametros))
        estadisticas_grupo = cursor.fetchall()

        # 4. Resumen por Asignatura
        sql_asig = """
            SELECT 
                COALESCE(a.Asi_NomAsignatura, 'Tecnología e Informática') AS asignatura,
                COUNT(*) AS total,
                SUM(CASE WHEN r.Reg_Observacion = 'Presente' THEN 1 ELSE 0 END) AS presentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Ausente' THEN 1 ELSE 0 END) AS ausentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Tarde' THEN 1 ELSE 0 END) AS tardes
            FROM registroasistencia r
            INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
            LEFT JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
            LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            WHERE 1=1
        """
        if condiciones:
            sql_asig += " AND " + " AND ".join(condiciones)
        sql_asig += " GROUP BY a.Asi_CodAsignatura, a.Asi_NomAsignatura ORDER BY a.Asi_CodAsignatura;"

        cursor.execute(sql_asig, tuple(parametros))
        estadisticas_asignatura = cursor.fetchall()

        # 5. Resumen por Jornada
        sql_jornada = """
            SELECT 
                CASE 
                    WHEN TIME(r.Reg_FechaHoraIngreso) BETWEEN '13:00:00' AND '18:59:59' THEN 'Tarde'
                    ELSE 'Mañana'
                END AS jornada,
                COUNT(*) AS total,
                SUM(CASE WHEN r.Reg_Observacion = 'Presente' THEN 1 ELSE 0 END) AS presentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Ausente' THEN 1 ELSE 0 END) AS ausentes,
                SUM(CASE WHEN r.Reg_Observacion = 'Tarde' THEN 1 ELSE 0 END) AS tardes
            FROM registroasistencia r
            INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
            LEFT JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
            LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
            WHERE 1=1
        """
        if condiciones:
            sql_jornada += " AND " + " AND ".join(condiciones)
        sql_jornada += " GROUP BY (CASE WHEN TIME(r.Reg_FechaHoraIngreso) BETWEEN '13:00:00' AND '18:59:59' THEN 'Tarde' ELSE 'Mañana' END) ORDER BY jornada;"

        cursor.execute(sql_jornada, tuple(parametros))
        estadisticas_jornada = cursor.fetchall()

        # 6. Resumen por Docente (si aplica rol coordinador)
        estadisticas_docente = []
        if rol == 'coordinador':
            sql_doc = """
                SELECT 
                    CONCAT(d.Doc_Nombres, ' ', COALESCE(d.Doc_Apellidos, '')) AS docente,
                    COUNT(*) AS total,
                    SUM(CASE WHEN r.Reg_Observacion = 'Presente' THEN 1 ELSE 0 END) AS presentes,
                    SUM(CASE WHEN r.Reg_Observacion = 'Ausente' THEN 1 ELSE 0 END) AS ausentes,
                    SUM(CASE WHEN r.Reg_Observacion = 'Tarde' THEN 1 ELSE 0 END) AS tardes
                FROM registroasistencia r
                INNER JOIN estudiantes e ON r.Reg_CodEstudiante = e.Est_CodEstudiante
                INNER JOIN docentes d ON r.Reg_CodDocente = d.Doc_CodDocentes
                LEFT JOIN asignatura a ON d.Doc_Cod_Asignatura = a.Asi_CodAsignatura
                WHERE 1=1
            """
            if condiciones:
                sql_doc += " AND " + " AND ".join(condiciones)
            sql_doc += " GROUP BY d.Doc_CodDocentes, d.Doc_Nombres, d.Doc_Apellidos ORDER BY d.Doc_Apellidos, d.Doc_Nombres;"
            cursor.execute(sql_doc, tuple(parametros))
            estadisticas_docente = cursor.fetchall()

        cursor.close()
        conexion.close()

        filtros = {
            'fecha': fecha_filtro,
            'grado': grado_filtro,
            'grupo': grupo_filtro,
            'jornada': jornada_filtro,
            'docente': docente_filtro,
            'asignatura': asignatura_filtro,
            'modalidad': modalidad_filtro
        }

        return render_template(
            'estadisticas.html',
            totales=totales,
            porcentajes=porcentajes,
            estadisticas_grado=estadisticas_grado,
            estadisticas_grupo=estadisticas_grupo,
            estadisticas_asignatura=estadisticas_asignatura,
            estadisticas_jornada=estadisticas_jornada,
            estadisticas_docente=estadisticas_docente,
            filtros=filtros,
            grados=grados,
            grupos=grupos,
            docentes=docentes,
            asignaturas=asignaturas,
            jornadas=jornadas,
            modalidades=MODALIDADES_TECNICAS,
            fecha_filtro=fecha_filtro,
            rol=rol,
            usuario=usuario
        )

    except Exception as e:
        print(f"[ERROR ESTADISTICAS]: {e}")
        if conexion and conexion.is_connected():
            conexion.close()
        return render_template('login.html', error="Ocurrió un problema al calcular las estadísticas de asistencia.")


@app.route('/logout')
def logout():
    """
    Cierra la sesión destruyendo los datos almacenados y redirige al login.
    """
    session.clear()
    return redirect(url_for('login'))


# Iniciamos el servidor de Flask en el puerto 5000
if __name__ == '__main__':
    print("Servidor ASISTEC iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)
