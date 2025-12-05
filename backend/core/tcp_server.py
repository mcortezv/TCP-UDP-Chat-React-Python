import socket
import threading

class TCPServer(threading.Thread):
    def __init__(self, ip, port, controller):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.controller = controller
        self.clients = set()
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))
        self.server.listen()

    def broadcast(self, message, source_sock):
        try:
            decoded = message.decode()
            self.controller.history.append(decoded)
        except:
            pass

        for c in list(self.clients):
            if c != source_sock:
                try:
                    c.sendall(message)
                except:
                    try:
                        self.clients.remove(c)
                        c.close()
                    except:
                        pass


    def handle_client(self, conn, addr):
        self.clients.add(conn)
        while self.running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                self.broadcast(data, conn)
            except:
                break
        try:
            self.clients.remove(conn)
        except:
            pass
        try:
            conn.close()
        except:
            pass


    def stop(self):
        self.running = False
        try:
            self.server.close()
        except:
            pass
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.port))
            s.close()
        except:
            pass
        for c in list(self.clients):
            try:
                c.close()
            except:
                pass
        self.clients.clear()

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
            except:
                break
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
