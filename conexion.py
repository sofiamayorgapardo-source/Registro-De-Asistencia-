import mysql.connector

def obtener_conexion():
    """
    Función sencilla para conectarse a la base de datos MySQL en XAMPP.
    Retorna el objeto de conexión si todo sale bien, o None si hay un error.
    """
    try:
        conexion = mysql.connector.connect(
            host="localhost",       # Servidor local de XAMPP
            port=3306,              # Puerto estándar de MySQL
            user="root",            # Usuario por defecto de XAMPP
            password="",            # Contraseña por defecto (vacía)
            database="asistec"      # Nombre de nuestra base de datos
        )
        return conexion
    except mysql.connector.Error as error:
        print(f"Error al conectar con la base de datos: {error}")
        return None

# Bloque de prueba directa: se ejecuta solo cuando corremos este archivo directamente
if __name__ == "__main__":
    print("--- PROBANDO CONEXION A MYSQL ---")
    conexion = obtener_conexion()
    
    if conexion and conexion.is_connected():
        print("[OK] Conexion exitosa con la base de datos ASISTEC.")
        
        # Realizamos una consulta sencilla a la tabla estudiantes
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Est_CodEstudiante, Est_Nombre, Est_Apellido, Est_Correo FROM estudiantes;")
        estudiantes = cursor.fetchall()
        
        print(f"\nConsulta exitosa. Se encontraron {len(estudiantes)} estudiantes registrados:")
        for est in estudiantes:
            print(f" - Codigo: {est['Est_CodEstudiante']} | Nombre: {est['Est_Nombre']} {est['Est_Apellido']} | Correo: {est['Est_Correo']}")
        
        # Cerramos el cursor y la conexión
        cursor.close()
        conexion.close()
        print("\nConexion cerrada correctamente.")
    else:
        print("[ERROR] No se pudo conectar a la base de datos.")
