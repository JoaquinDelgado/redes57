import socket
import sys
import subprocess
import threading
import time

detener_vlc = threading.Event()


def sendAll(comando, socket):
    total_sent = 0
    while total_sent < comando.__sizeof__():
        bytes_sent = socket.send(comando[total_sent:])
        if bytes_sent == 0:
            break
        total_sent += bytes_sent


def abrir_vlc(comando):
    global detener_vlc
    proceso_vlc = subprocess.Popen(
        comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        if detener_vlc.is_set():
            proceso_vlc.terminate()
            proceso_vlc.wait()
            break


def main():
    argv = sys.argv
    print(argv)
    server_port = int(sys.argv[2])
    server_ip = sys.argv[1]
    puerto_vlc = int(sys.argv[3])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    thread_vlc = None

    while True:
        comando = input("Ingrese el comando: ")

        if (comando == "DESCONECTAR"):
            if thread_vlc is not None:
                detener_vlc.set()
                thread_vlc.join()
            comando = f"{comando}\r\n".encode()
            sendAll(comando, client_socket)
            client_socket.close()
            sys.exit(0)
        elif (comando == "INTERRUMPIR"):
            comando = f"{comando}\r\n".encode()
            sendAll(comando, client_socket)
            respuestaServidor(client_socket)
        elif (comando == "CONTINUAR"):
            comando = f"{comando}\r\n".encode()
            sendAll(comando, client_socket)
            respuestaServidor(client_socket)
        elif comando == "CONECTAR":
            if thread_vlc is not None and thread_vlc.is_alive():
                print("VLC ya está en ejecución.")
            else:
                comando = f"{comando} {puerto_vlc}\r\n".encode()
                local_ip = client_socket.getsockname()[0]
                comandoVar = "vlc rtp://"+local_ip+":"+puerto_vlc.__str__()
                thread_vlc = threading.Thread(
                    target=abrir_vlc, args=(comandoVar,))
                thread_vlc.start()
                time.sleep(1)
                sendAll(comando, client_socket)
                respuestaServidor(client_socket)
        else:
            print("Comando no reconocido")


def respuestaServidor(client_socket):
    respuesta = client_socket.recv(1024).decode()
    if (respuesta == "OK\n"):
        print(respuesta)


if __name__ == "__main__":
    main()
