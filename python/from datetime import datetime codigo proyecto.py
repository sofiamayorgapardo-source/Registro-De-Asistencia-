from datetime import datetime


# ==============================
# DATOS DEL SISTEMA
# ==============================

usuarios = {
    "docente1": {
        "password": "1234",
        "nombre": "Docente Principal",
        "rol": "docente"
    },
    "coordinador": {
        "password": "admin123",
        "nombre": "Coordinador",
        "rol": "coordinador"
    }
}

estudiantes = [
    {
        "id": 1,
        "nombre": "Juan Pérez",
        "grado": "10",
        "grupo": "A"
    },
    {
        "id": 2,
        "nombre": "María López",
        "grado": "10",
        "grupo": "A"
    },
    {
        "id": 3,
        "nombre": "Carlos Rodríguez",
        "grado": "10",
        "grupo": "A"
    }
]

asistencias = []


# ==============================
# INICIO DE SESIÓN
# ==============================

def iniciar_sesion():
    print("\n==============================")
    print("          ASISTEC")
    print("==============================")

    usuario = input("Usuario: ")
    password = input("Contraseña: ")

    if usuario in usuarios and usuarios[usuario]["password"] == password:
        print("\nInicio de sesión exitoso.")
        print("Bienvenido:", usuarios[usuario]["nombre"])

        return usuarios[usuario]

    print("\nUsuario o contraseña incorrectos.")
    return None


# ==============================
# REGISTRAR ASISTENCIA
# ==============================

def registrar_asistencia(usuario):
    print("\n==============================")
    print("     REGISTRO DE ASISTENCIA")
    print("==============================")

    print("\nEstudiantes:")

    for estudiante in estudiantes:
        print(
            f'{estudiante["id"]}. '
            f'{estudiante["nombre"]} - '
            f'Grado {estudiante["grado"]} '
            f'Grupo {estudiante["grupo"]}'
        )

    for estudiante in estudiantes:

        print("\nEstudiante:", estudiante["nombre"])

        print("1. Presente")
        print("2. Ausente")
        print("3. Tarde")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            estado = "Presente"

        elif opcion == "2":
            estado = "Ausente"

        elif opcion == "3":
            estado = "Tarde"

        else:
            print("Opción inválida.")
            continue

        registro = {
            "estudiante_id": estudiante["id"],
            "estudiante": estudiante["nombre"],
            "estado": estado,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "hora": datetime.now().strftime("%H:%M:%S"),
            "usuario": usuario["nombre"]
        }

        asistencias.append(registro)

    print("\nAsistencia registrada correctamente.")


# ==============================
# CONSULTAR ASISTENCIA
# ==============================

def consultar_asistencia():
    print("\n==============================")
    print("     CONSULTA DE ASISTENCIA")
    print("==============================")

    if len(asistencias) == 0:
        print("No existen registros.")
        return

    for registro in asistencias:
        print("\n------------------------------")
        print("Estudiante:", registro["estudiante"])
        print("Estado:", registro["estado"])
        print("Fecha:", registro["fecha"])
        print("Hora:", registro["hora"])
        print("Registrado por:", registro["usuario"])


# ==============================
# MENÚ DEL DOCENTE
# ==============================

def menu_docente(usuario):

    while True:

        print("\n==============================")
        print("       MENÚ DOCENTE")
        print("==============================")

        print("1. Registrar asistencia")
        print("2. Consultar asistencia")
        print("3. Cerrar sesión")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            registrar_asistencia(usuario)

        elif opcion == "2":
            consultar_asistencia()

        elif opcion == "3":
            print("\nSesión cerrada.")
            break

        else:
            print("\nOpción inválida.")


# ==============================
# MENÚ DEL COORDINADOR
# ==============================

def menu_coordinador(usuario):

    while True:

        print("\n==============================")
        print("     MENÚ COORDINADOR")
        print("==============================")

        print("1. Consultar asistencia")
        print("2. Ver todos los registros")
        print("3. Cerrar sesión")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            consultar_asistencia()

        elif opcion == "2":
            consultar_asistencia()

        elif opcion == "3":
            print("\nSesión cerrada.")
            break

        else:
            print("\nOpción inválida.")


# ==============================
# PROGRAMA PRINCIPAL
# ==============================

def main():

    usuario = iniciar_sesion()

    if usuario is None:
        return

    if usuario["rol"] == "docente":
        menu_docente(usuario)

    elif usuario["rol"] == "coordinador":
        menu_coordinador(usuario)


# Ejecutar programa
if __name__ == "__main__":
    main()