import socket
import threading

class UDPServer(threading.Thread):
    def __init__(self, ip, port, controller):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.controller = controller
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((ip, port))
        self.running = True
        self.clients = set()


    def run(self):
        while self.running:
            try:
                data, addr = self.server.recvfrom(1024)
            except:
                break
            try:
                decoded = data.decode()
                self.controller.history.append(decoded)
            except:
                pass
            self.clients.add(addr)
            for c in list(self.clients):
                if c != addr:
                    try:
                        self.server.sendto(data, c)
                    except:
                        try:
                            self.clients.remove(c)
                        except:
                            pass


    def stop(self):
        self.running = False
        try:
            self.server.close()
        except:
            pass
