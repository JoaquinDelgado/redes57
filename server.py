import socket
import threading as th
import sys
import time
import signal


global_list = []
global_list_lock = th.Lock()
threads = []
server_socket = None
client_sockets = []

# Función para agregar elementos a la lista global


def add_to_global_list(item):
    global global_list
    with global_list_lock:
        global_list.append(item)
    return global_list.index(item)

# Función para eliminar elementos de la lista global


def remove_from_global_list(indice):
    global global_list
    with global_list_lock:
        global_list.pop(indice)

# Función para cambiar el booleano de un item por indice


def change_item_bool(indice, bool):
    global global_list
    with global_list_lock:
        global_list[indice] = (global_list[indice][0], bool)


def main():
    global server_socket
    global threads
    global client_sockets
    if len(sys.argv) != 3:
        print("Uso: python server.py <ServerIP> <ServerPort>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    # Crear un socket para el servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((server_ip, server_port))

    server_socket.listen(5)

    print(f"Servidor escuchando en {server_ip}:{server_port}")

    thread = th.Thread(target=escucharVLC, args=())
    thread.start()
    print(thread)
    threads.append(thread)

    while not exit_flag.is_set():
        client_socket, client_address = server_socket.accept()
        client_sockets.append(client_socket)
        # client_socket.settimeout(2)
        print(f"Conexión entrante de {client_address}")

        # Manejar la conexión con el cliente en un hilo o proceso separado si es necesario
        thread = th.Thread(target=handle_client, args=(
            client_socket, client_address,))
        thread.start()
        threads.append(thread)


# escucha rtp en el puerto 1234 en localhost
def escucharVLC():
    server_ip = '127.0.0.1'
    server_port = 65534

    # Crea un socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((server_ip, server_port))

    while not exit_flag.is_set():
        try:
            # Recibe un paquete RTP
            data, addr = sock.recvfrom(3984)

            # Envio a todos los clientes en la lista global
            with global_list_lock:
                for item in global_list:
                    if item[1] == False:
                        try:
                            item[0].send(data)
                        except (ConnectionRefusedError, ConnectionResetError):
                            global_list.pop(global_list.index(item))

        except KeyboardInterrupt:
            print("Deteniendo la recepción del flujo RTP por UDP...")
            break
    sock.close()

# Función para manejar la señal SIGINT (Ctrl+C)


def signal_handler(sig, frame):
    global server_socket
    global threads
    global client_sockets
    print("Señal SIGINT recibida. Cerrando el programa...")
    # Agrega cualquier lógica de limpieza que necesites aquí
    # Indicamos a los hilos que deben salir

    exit_flag.set()
    print("Esperando a que los hilos terminen...")

    for client_socket in client_sockets:
        print(client_socket)
        client_socket.close()

    print(threads.__len__())
    for thread in threads:
        print(thread)
        if thread:
            thread.join()

    print(server_socket)
    server_socket.close()

    print("Programa cerrado correctamente.")
    sys.exit(0)

    # Creamos una bandera para indicar a los hilos que deben salir
exit_flag = th.Event()

# Registramos el manejador de señal para SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


##
def handle_client(client_socket, client_address):
    indice = -1
    command = ""
    while not exit_flag.is_set():
        while not exit_flag.is_set():
            # Recibir datos del cliente
            try:
                data = client_socket.recv(1024).decode()
            except:
                break
            # except socket.timeout:
            #   break
            command += data
            if (command.find("\r\n") != -1):
                command = command.replace("\r\n", "")
                break
        # Cerrar la conexión con el cliente
        if (command == "DESCONECTAR"):
            remove_from_global_list(indice)
            client_socket.close()
            break
        if (command.find("CONECTAR") != -1):
            puerto = command.replace(" ", "")
            puerto = command.replace("CONECTAR", "")
            print(f"Conectando al puerto {puerto}")
            print(client_address)
            print(puerto)
            # checkear si el puerto es valido
            try:
                # Inicio conexion udp al puerto especificado
                if (int(puerto) > 1024 and int(puerto) < 65535):
                    udp_socket = socket.socket(
                        socket.AF_INET, socket.SOCK_DGRAM)
                    udp_socket.connect((client_address[0], int(puerto)))
                    # Agregar el socket a la lista global
                    indice = add_to_global_list((udp_socket, False))
                    client_socket.send('OK\n'.encode())

                else:
                    raise Exception
            except:
                print("Puerto invalido")
                client_socket.send('ERROR\n'.encode())

        if (command == "INTERRUMPIR"):
            if indice >= 0 and indice < len(global_list):
                change_item_bool(indice, True)
                print('ip cliente ' + global_list[indice][0].getpeername()[0])
                print('interrumpiendo cliente ' + str(indice))
            client_socket.send('OK\n'.encode())

        if (command == "CONTINUAR"):
            if indice >= 0 and indice < len(global_list):
                change_item_bool(indice, False)
                print('ip cliente ' + global_list[indice][0].getpeername()[0])
                print('continuando cliente ' + str(indice))
            client_socket.send('OK\n'.encode())
        command = ""


if __name__ == "__main__":
    main()
