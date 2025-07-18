from abc import ABC, abstractmethod
from datetime import datetime, time

# Excepciones Personalizadas
class ReservaDuplicadaException(Exception):
    pass

class UsuarioNoAutorizadoException(Exception):
    pass

# Clase Abstracta
class ReservaBase(ABC):
    @abstractmethod
    def calcular_duracion(self):
        pass

# Clase Persona (herencia)
class Persona:
    def __init__(self, nombre):
        self.__nombre = nombre

    def get_nombre(self):
        return self.__nombre

class Usuario(Persona):
    def __init__(self, username, password):
        super().__init__(username)  # Hereda como nombre
        self.__username = username
        self.__password = password

    def verificar_password(self, password):
        return self.__password == password

    def get_username(self):
        return self.__username

class EquipoMac:
    def __init__(self, codigo_identificativo, marca):
        self.__codigo_identificativo = codigo_identificativo
        self.__marca = marca
        self.__estado = "disponible"
        self.__historial_reservas = []

    def get_estado(self):
        return self.__estado

    def get_codigo(self):
        return self.__codigo_identificativo

    def agregar_reserva_historial(self, reserva):
        self.__historial_reservas.append(reserva)

    def set_estado(self, estado):
        self.__estado = estado

class Reserva(ReservaBase):
    def __init__(self, id_reserva, equipo, usuario, fecha, turno, hora_inicio, hora_fin):
        self.__id_reserva = id_reserva
        self.__equipo = equipo
        self.__usuario = usuario
        self.__fecha = fecha
        self.__turno = turno
        self.__hora_inicio = hora_inicio
        self.__hora_fin = hora_fin
        self.__estado = "activa"

    def calcular_duracion(self):
        fmt = "%H:%M"
        h_inicio = datetime.strptime(self.__hora_inicio, fmt)
        h_fin = datetime.strptime(self.__hora_fin, fmt)
        duracion = h_fin - h_inicio
        horas = duracion.seconds // 3600
        return f"{horas} horas"

    def get_usuario(self):
        return self.__usuario

    def get_equipo(self):
        return self.__equipo

    def get_id(self):
        return self.__id_reserva

    def get_fecha(self):
        return self.__fecha

    def get_turno(self):
        return self.__turno

    def get_estado(self):
        return self.__estado

    def set_estado(self, estado):
        self.__estado = estado

    def __str__(self):
        return f"{self.__id_reserva} - {self.__equipo.get_codigo()} ({self.__fecha} {self.__turno})"

class SistemaReserva:
    def __init__(self):
        self.__usuarios = []
        self.__equipos = []
        self.__reservas = []
        self.__usuario_actual = None
        self.inicializar_datos()

    def inicializar_datos(self):
        self.__usuarios = [
            Usuario("acxell", "1234"),
            Usuario("daniel", "4321"),
            Usuario("renato", "5678")
        ]

        marcas = ["MacBook Pro", "iMac", "Mac Studio", "Mac Mini", "MacBook Air", "Mac Pro"]
        for i, marca in enumerate(marcas):
            self.__equipos.append(EquipoMac(f"MAC-{i+1}", marca))

    def autenticar_usuario(self, username, password):
        for usuario in self.__usuarios:
            if usuario.get_username() == username and usuario.verificar_password(password):
                self.__usuario_actual = usuario
                return True
        raise UsuarioNoAutorizadoException("Usuario o contraseña incorrectos.")

    def generar_id_reserva(self):
        return f"R-{len(self.__reservas)+1}"

    def mostrar_equipos_disponibles(self, fecha, turno):
        disponibles = []
        for equipo in self.__equipos:
            disponible = True
            for reserva in self.__reservas:
                if (reserva.get_equipo() == equipo and reserva.get_fecha() == fecha and reserva.get_turno() == turno and reserva.get_estado() == "activa"):
                    disponible = False
                    break
            if disponible:
                disponibles.append(equipo)
        return disponibles

    def realizar_reserva(self, equipo, fecha, turno, hora_inicio, hora_fin):
        for reserva in self.__reservas:
            if (reserva.get_equipo() == equipo and reserva.get_fecha() == fecha and reserva.get_turno() == turno and reserva.get_estado() == "activa"):
                raise ReservaDuplicadaException("Ya existe una reserva activa para este equipo en ese turno.")

        id_reserva = self.generar_id_reserva()
        reserva = Reserva(id_reserva, equipo, self.__usuario_actual, fecha, turno, hora_inicio, hora_fin)
        self.__reservas.append(reserva)
        equipo.set_estado("reservado")
        equipo.agregar_reserva_historial(reserva)
        print(f"✅ Reserva registrada: {reserva}")

    def mis_reservas(self):
        return [r for r in self.__reservas if r.get_usuario() == self.__usuario_actual and r.get_estado() == "activa"]

    def registrar_devolucion(self, id_reserva):
        for reserva in self.__reservas:
            if reserva.get_id() == id_reserva and reserva.get_usuario() == self.__usuario_actual:
                reserva.set_estado("finalizada")
                reserva.get_equipo().set_estado("disponible")
                print("✅ Devolución registrada.")
                return
        print("⚠️ Reserva no encontrada o no corresponde al usuario actual.")

# Menú principal
def main():
    sistema = SistemaReserva()
    print("=== BIENVENIDO AL SISTEMA DE RESERVAS MAC DE VML ===")
    try:
        username = input("Usuario: ")
        password = input("Contraseña: ")
        sistema.autenticar_usuario(username, password)
    except UsuarioNoAutorizadoException as e:
        print(e)
        return

    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Reservar equipo")
        print("2. Mis reservas")
        print("3. Registrar devolución")
        print("4. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            fecha = input("Fecha (DD-MM-YYYY): ")
            turno = input("Turno (mañana/tarde): ").lower()

            if turno not in ("mañana", "tarde"):
                print("Turno inválido. Solo 'mañana' o 'tarde'.")
                continue

            equipos = sistema.mostrar_equipos_disponibles(fecha, turno)
            if not equipos:
                print("❌ No hay equipos disponibles.")
                continue

            print("Equipos disponibles:")
            for i, eq in enumerate(equipos):
                print(f"{i + 1}. {eq.get_codigo()} - {eq._EquipoMac__marca}")

            try:
                seleccion = int(input("Selecciona el número del equipo: ")) - 1
                if seleccion < 0 or seleccion >= len(equipos):
                    print("Selección inválida.")
                    continue
            except ValueError:
                print("Debe ingresar un número válido.")
                continue

            if turno == "mañana":
                hora_inicio = "08:00"
                hora_fin = "17:00"
            else:
                hora_inicio = "12:00"
                hora_fin = "21:00"

            try:
                sistema.realizar_reserva(equipos[seleccion], fecha, turno, hora_inicio, hora_fin)
            except ReservaDuplicadaException as e:
                print(f"⚠️ {e}")
        elif opcion == "2":
            reservas = sistema.mis_reservas()
            if reservas:
                for r in reservas:
                    duracion = r.calcular_duracion()
                    print(f"{r} | Duración: {duracion}")
            else:
                print("No tienes reservas activas.")
        elif opcion == "3":
            id_reserva = input("Ingrese ID de la reserva a devolver: ")
            sistema.registrar_devolucion(id_reserva)
        elif opcion == "4":
            print("👋 Cerrando sesión. ¡Hasta luego!")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
