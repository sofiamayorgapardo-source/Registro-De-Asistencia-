# -*- coding: utf-8 -*-
import mysql.connector

def obtener_conexion():
    """
    Función para conectarse a la base de datos MySQL en XAMPP.
    Retorna el objeto de conexión activo o None si ocurre un error.
    """
    try:
        conexion = mysql.connector.connect(
            host="localhost",       # Servidor local XAMPP
            port=3306,              # Puerto MySQL
            user="root",            # Usuario estándar
            password="",            # Contraseña por defecto vacía
            database="asistec",     # Base de datos oficial
            charset="utf8mb4"
        )
        return conexion
    except mysql.connector.Error as error:
        print(f"[ERROR CONEXION MYSQL]: {error}")
        return None

if __name__ == "__main__":
    print("Probando conexion a MySQL (asistec)...")
    c = obtener_conexion()
    if c and c.is_connected():
        print("[OK] Conexion exitosa a la base de datos asistec.")
        c.close()
    else:
        print("[ERROR] No se pudo conectar.")
