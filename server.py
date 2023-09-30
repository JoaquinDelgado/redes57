import socket
import threading as th
import sys
import time




def main():
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
            client_socket.send('OK\n'.encode())
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
                    while True:
                        time.sleep(1)
                        udp_socket.send("Hola".encode())
                else:
                    raise Exception
            except:
                print("Puerto invalido")
                client_socket.send('ERROR\n'.encode())

        if (command == "INTERRUMPIR"):
            print('interrumpiendo')
            client_socket.send('OK\n'.encode())
        if (command == "CONTINUAR"):
            print('continuando')
            client_socket.send('OK\n'.encode())
        
        command = ""


if __name__ == "__main__":
    main()