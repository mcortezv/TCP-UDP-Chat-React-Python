import socket
import threading

class UDPServer(threading.Thread):

    def __init__(self, ip, port, global_clients):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.clients = global_clients
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((ip, port))

    def run(self):
        print("Servidor UDP escuchando en", self.ip, "puerto", self.port)
        while True:
            data, addr = self.server.recvfrom(1024)

            self.clients.add(addr)

            for c in self.clients:
                if c != addr:
                    self.server.sendto(data, c)
