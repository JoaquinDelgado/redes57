import socket
import threading as th
import sys
import time

global_list = []
global_list_lock = th.Lock()

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
    # Crear una lista global compartida
    
    # Obtener la dirección IP del servidor y el puerto desde los argumentos de línea de comandos
    if len(sys.argv) != 3:
        print("Uso: python server.py <ServerIP> <ServerPort>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    # Crear un socket para el servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Enlazar el socket al servidor IP y puerto
    server_socket.bind((server_ip, server_port))

    # Escuchar conexiones entrantes (se permite un máximo de 5 conexiones en espera)
    server_socket.listen(5)

    print(f"Servidor escuchando en {server_ip}:{server_port}")

    th.Thread(target=escucharVLC, args=()).start()

    # Aceptar conexiones de clientes
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexión entrante de {client_address}")

        # Manejar la conexión con el cliente en un hilo o proceso separado si es necesario
        th.Thread(target=handle_client, args=(client_socket,client_address,)).start()
      

### escucha rtp en el puerto 1234 en localhost
def escucharVLC():
    server_ip = 'localhost'
    server_port = 1234

    # Crea un socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enlaza el socket a la dirección del servidor RTP
    sock.bind((server_ip, server_port))

    while True:
        try:
            # Recibe un paquete RTP
            data, addr = sock.recvfrom(3984)
            

            # Envio a todos los clientes en la lista global
            with global_list_lock:
                for item in global_list:
                    if item[1] == False:
                        item[0].send(data)

        except KeyboardInterrupt:
            print("Deteniendo la recepción del flujo RTP por UDP...")
            break
    sock.close()



##         
def handle_client(client_socket, client_address):
    indice = -1
    command = ""
    while True:
        while True:
        # Recibir datos del cliente
            data = client_socket.recv(1024).decode()
            command += data
            if (command.find("\r\n") != -1):
                command = command.replace("\r\n", "")
                break
        print(f"Datos recibidos: {command}")
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
            #checkear si el puerto es valido
            try:
            # Inicio conexion udp al puerto especificado
                if (int(puerto) > 1024 and int(puerto) < 65535):
                    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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