import socket
import threading

class TCPServer(threading.Thread):

    def __init__(self, ip, port, global_clients):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.clients = global_clients
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen()

    def broadcast(self, message, source):
        for c in list(self.clients):
            if c != source:
                try:
                    c.sendall(message)
                except:
                    self.clients.remove(c)

    def handle_client(self, conn, addr):
        print("Cliente conectado", addr)
        self.clients.add(conn)

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                self.broadcast(data, conn)
            except:
                break

        self.clients.remove(conn)
        conn.close()

    def run(self):
        print("Servidor TCP escuchando en puerto", self.port)
        while True:
            conn, addr = self.server.accept()
            threading.Thread(
                target=self.handle_client,
                args=(conn, addr),
                daemon=True
            ).start()
