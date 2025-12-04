import socket
import threading

HOST = "192.168.0.3"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print("Servidor UDP escuchando en", HOST, "puerto", PORT)

clients = set()

# bucle para recibir y reenviar
while True:
    data, addr = server.recvfrom(1024)

    # registrar cliente si no esta
    clients.add(addr)

    # reenviar mensaje a todos menos al que lo envio
    for c in clients:
        if c != addr:
            server.sendto(data, c)
