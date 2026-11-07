# -*- coding: utf-8 -*-
import os
import mysql.connector

# Cargar variables opcionales desde .env en desarrollo sin sobrescribir variables de entorno de producción (Render)
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except Exception:
    pass

def obtener_conexion():
    """
    Función para conectarse a la base de datos MySQL (local en XAMPP o remota en la nube).
    Retorna el objeto de conexión activo o None si ocurre un error.
    """
    try:
        host = os.environ.get("DB_HOST", "localhost")
        port = int(os.environ.get("DB_PORT", 3306))
        user = os.environ.get("DB_USER", "root")
        password = os.environ.get("DB_PASSWORD", "")
        database = os.environ.get("DB_NAME", "asistec")

        config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": "utf8mb4"
        }

        # Soporte seguro SSL/TLS para Aiven u otros proveedores en la nube
        ssl_mode = os.environ.get("DB_SSL_MODE", "").strip().upper()
        ssl_ca = os.environ.get("DB_SSL_CA", "").strip()

        if ssl_ca and os.path.exists(ssl_ca):
            config["ssl_ca"] = ssl_ca
            config["ssl_verify_cert"] = True
        elif ssl_mode in ("REQUIRED", "VERIFY_CA", "VERIFY_IDENTITY"):
            config["ssl_disabled"] = False

        conexion = mysql.connector.connect(**config)
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
