# Joaquin Delgado 45464043
# Joaquin Gonzalez 51648875
# Valery Nater 48177512

import socket
import threading as th
import sys
import signal
import time

global_list = []
global_list_lock = th.Lock()
threads = []
server_socket = None
client_sockets = []


def sendAll(comando, socket):
    total_sent = 0
    while total_sent < comando.__sizeof__():
        bytes_sent = socket.send(comando[total_sent:])
        if bytes_sent == 0:
            break
        total_sent += bytes_sent


def add_to_global_list(item):
    with global_list_lock:
        global_list.append(item)
    return global_list.index(item)


def remove_from_global_list(indice):
    with global_list_lock:
        if 0 <= indice < len(global_list):
            item = global_list.pop(indice)
            if item:
                item[0].close()


def change_item_bool(indice, bool):
    with global_list_lock:
        if 0 <= indice < len(global_list):
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

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(5)
        print(f"Servidor escuchando en {server_ip}:{server_port}")

        thread = th.Thread(target=escucharVLC, args=())
        thread.start()
        threads.append(thread)

        while not exit_flag.is_set():
            client_socket, client_address = server_socket.accept()
            client_sockets.append(client_socket)
            print(f"Conexión entrante de {client_address}")

            thread = th.Thread(target=handle_client, args=(
                client_socket, client_address,))
            thread.start()
            threads.append(thread)

    except Exception as e:
        pass


def escucharVLC():
    server_ip = '127.0.0.1'
    server_port = 65534
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((server_ip, server_port))

    while not exit_flag.is_set():
        try:
            data, addr = sock.recvfrom(1328)

            with global_list_lock:
                for item in global_list:
                    if item[1] == False:
                        try:
                            item[0].send(data)
                        except (ConnectionRefusedError, ConnectionResetError) as exception:
                            global_list.pop(global_list.index(item))

        except KeyboardInterrupt:
            print("Deteniendo la recepción del flujo RTP por UDP...")
            break
    sock.close()


def signal_handler(sig, frame):
    global server_socket
    global threads
    global client_sockets
    print("Señal SIGINT recibida. Cerrando el programa...")

    exit_flag.set()

    for client_socket in client_sockets:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()

    for thread in threads:
        if thread and thread.is_alive():
            thread.join()

    if server_socket:
        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()

    print("Programa cerrado correctamente.")
    time.sleep(1)
    sys.exit(0)


exit_flag = th.Event()
signal.signal(signal.SIGINT, signal_handler)


def handle_client(client_socket, client_address):
    indice = -1
    command = ""
    while not exit_flag.is_set():
        while not exit_flag.is_set():
            try:
                data = client_socket.recv(1024).decode()
            except:
                break
            command += data
            if (command.find("\r\n") != -1):
                command = command.replace("\r\n", "")
                break
        if (command == "DESCONECTAR"):
            remove_from_global_list(indice)
            client_socket.close()
            break
        if (command.find("CONECTAR") != -1):
            puerto = command.replace("CONECTAR", "")
            print(f"Conectando al puerto {puerto}")
            print(client_address)
            try:
                if (int(puerto) > 1024 and int(puerto) < 65535):
                    udp_socket = socket.socket(
                        socket.AF_INET, socket.SOCK_DGRAM)
                    udp_socket.connect((client_address[0], int(puerto)))
                    indice = add_to_global_list((udp_socket, False))
                    comando = 'OK\n'.encode()
                    sendAll(comando, client_socket)

                else:
                    raise Exception
            except:
                print("Puerto invalido")
                comando = 'ERROR\n'.encode()
                sendAll(comando, client_socket)

        if (command == "INTERRUMPIR"):
            if indice >= 0 and indice < len(global_list):
                change_item_bool(indice, True)
                print('ip cliente ' + global_list[indice][0].getpeername()[0])
                print('interrumpiendo cliente ' + str(indice))
            comando = 'OK\n'.encode()
            sendAll(comando, client_socket)

        if (command == "CONTINUAR"):
            if indice >= 0 and indice < len(global_list):
                change_item_bool(indice, False)
                print('ip cliente ' + global_list[indice][0].getpeername()[0])
                print('continuando cliente ' + str(indice))
            comando = 'OK\n'.encode()
            sendAll(comando, client_socket)
        command = ""
    client_socket.close()


if __name__ == "__main__":
    main()
