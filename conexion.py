
# -*- coding: utf-8 -*-
import os
import mysql.connector

# Cargar variables de entorno desde .env sin sobrescribir
# las variables configuradas en producción (Render).
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass


def obtener_conexion():
    """
    Conecta ASISTEC con MySQL local (XAMPP)
    o TiDB Cloud mediante SSL.
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

        # Configuración SSL para TiDB Cloud.
        ssl_ca = os.environ.get("DB_SSL_CA", "").strip()

        if ssl_ca:
            if not os.path.isfile(ssl_ca):
                raise FileNotFoundError(
                    "No se encontró el certificado SSL: " + ssl_ca
                )

            config.update({
                "ssl_ca": ssl_ca,
                "ssl_verify_cert": True,
                "ssl_verify_identity": True
            })

        conexion = mysql.connector.connect(**config)

        return conexion

    except (mysql.connector.Error, OSError, ValueError) as error:
        print(f"[ERROR CONEXION MYSQL]: {error}")
        return None


if __name__ == "__main__":
    print("Probando conexión a la base de datos ASISTEC...")

    c = obtener_conexion()

    if c and c.is_connected():
        print("[OK] Conexión exitosa a ASISTEC.")
        c.close()
    else:
        print("[ERROR] No se pudo conectar.")
