import socket
import threading

# servidor tcp
HOST = '192.168.0.3'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

# envia el mensaje a los demas clientes
def broadcast(message, source):
    for c in clients:
        if c != source:
            try:
                c.sendall(message)
            except:
                clients.remove(c)

# maneja cada cliente conectado
def handle_client(conn, addr):
    print("Cliente conectado", addr)
    clients.append(conn)

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            broadcast(data, conn)
        except:
            break

    clients.remove(conn)
    conn.close()

print("Servidor TCP escuchando en puerto", PORT)

# acepta clientes
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
