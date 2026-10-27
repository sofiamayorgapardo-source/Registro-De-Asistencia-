# =========================================================================
# SISTEMA ASISTEC - APLICACIÓN PRINCIPAL INTEGRADA
# =========================================================================

from flask import Flask, jsonify
from conexion import inicializar_tablas, conectar_bd

app = Flask(__name__)

# Configuración de datos institucionales de prueba
MODALIDADES_TECNICAS = ["Desarrollo de Software", "Sistemas", "Contabilidad", "Gestión Empresarial"]
ASIGNATURAS_GENERALES = ["Matemáticas", "Español", "Inglés", "Ciencias Naturales"]
ASIGNATURAS_TODAS = ASIGNATURAS_GENERALES + ["Programación", "Base de Datos", "Contabilidad Básica"]

@app.route('/')
def home():
    return jsonify({
        "mensaje": "Bienvenido al Sistema ASISTEC — API Integrada",
        "estado": "Activo y funcionando"
    })

@app.route('/api/estado_sistema')
def api_estado_sistema():
    """
    API de diagnóstico institucional que devuelve el estado actual del servidor,
    la modalidad activa y un resumen rápido de las reglas académicas cargadas.
    """
    # Verificamos la conexión a la base de datos en tiempo real
    conexion = conectar_bd()
    db_estado = "Conectada y operativa" if conexion else "Sin conexión"
    if conexion:
        conexion.close()

    return jsonify({
        "sistema": "ASISTEC — Sistema Inteligente de Registro de Asistencia Estudiantil",
        "estado": "Operativo y conectado",
        "version": "2.0-beta",
        "base_de_datos": db_estado,
        "modalidades_soportadas": MODALIDADES_TECNICAS,
        "total_asignaturas_generales": len(ASIGNATURAS_GENERALES),
        "total_asignaturas_totales": len(ASIGNATURAS_TODAS),
        "mensaje": "Integración completa de Base de Datos y API realizada con éxito."
    })

if __name__ == '__main__':
    print("Inicializando base de datos de ASISTEC...")
    inicializar_tablas()
    app.run(debug=True, port=5000)
