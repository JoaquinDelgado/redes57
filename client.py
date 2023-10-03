import socket
import sys


def main():
    argv = sys.argv
    print(argv)
    server_port = int(sys.argv[2])
    server_ip = sys.argv[1]
    puerto_vlc = int(sys.argv[3])

    # Crear un socket para el cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Leer la IP y puerto del servidor de los argumentos de linea de commando

    # Conectar el socket al servidor
    client_socket.connect((server_ip, server_port))

    while True:
        comando = input("Ingrese el comando: ")

        if (comando == "DESCONECTAR"):
            client_socket.send(f"{comando}\r\n".encode())
            client_socket.close()
            sys.exit(1)
        elif (comando == "INTERRUMPIR"):
            client_socket.send(f"{comando}\r\n".encode())
            respuestaServidor(client_socket)
        elif (comando == "CONTINUAR"):
            client_socket.send(f"{comando}\r\n".encode())
            respuestaServidor(client_socket)
        elif comando == "CONECTAR":
            client_socket.send(f"{comando} {puerto_vlc}\r\n".encode())
            respuestaServidor(client_socket)
        else:
            print("Comando no reconocido")


def respuestaServidor(client_socket):
    respuesta = client_socket.recv(1024).decode()
    if (respuesta == "OK\n"):
        print(respuesta)


if __name__ == "__main__":
    main()
