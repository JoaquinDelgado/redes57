import socket
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
        # Aquí puedes agregar la lógica para comunicarte con el cliente

        # Ejemplo: Enviar un mensaje de bienvenida al cliente
        welcome_message = "¡Bienvenido al servidor!"
        client_socket.send(welcome_message.encode())

        # Cerrar la conexión con el cliente
        client_socket.close()

if __name__ == "__main__":
    main()