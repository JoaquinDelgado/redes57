import socket
import threading as th


def main():
    # Obtener la dirección IP del servidor y el puerto desde los argumentos de línea de comandos
    import sys
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

    # Aceptar conexiones de clientes
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexión entrante de {client_address}")

        # Manejar la conexión con el cliente en un hilo o proceso separado si es necesario
        th.Thread(target=handle_client, args=(client_socket,client_address,)).start()

        # # Logica para cerrar el servidor
        # if input("Presione 'q' para cerrar el servidor: ") == 'q':
        #     break

    server_socket.close()
        

##         
def handle_client(client_socket, client_address):

    exit = False
    command = ""
    while not exit:
        while True:
        # Recibir datos del cliente
            data = client_socket.recv(1024).decode()
            command += data
            if (command.find("\r\n") != -1):
                command = command.replace("\r\n", "")
                break
        print(f"Datos recibidos: {command}")
        # Cerrar la conexión con el cliente
        
        if (command.find("CONECTAR") != -1):
            puerto = command.replace("CONECTAR ", "")
            # Inicio conexion udp al puerto especificado
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.bind((client_address, int(puerto)))

        if (command == "INTERRUMPIR"):
            print('interrumpiendo')
        if (command == "CONTINUAR"):
            print('continuando')

        if (command == "DESCONECTAR"):
            client_socket.close()
            exit = True
        command = ""


if __name__ == "__main__":
    main()