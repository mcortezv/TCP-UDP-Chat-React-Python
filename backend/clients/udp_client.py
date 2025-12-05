import socket
import threading
import time

class UDPClient:
    def __init__(self, username, host, port, controller):
        self.username = username
        self.host = host
        self.port = port
        self.controller = controller
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0))
        self.running = True
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()

    def _recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                try:
                    txt = data.decode()
                    self.controller.history.append(txt)
                except:
                    pass
            except:
                break

    def start(self):
        pass

    def send(self, message: str):
        payload = f"{self.username}: {message}|{time.time()}".encode()
        try:
            self.sock.sendto(payload, (self.host, self.port))
        except:
            pass

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass

    def switch_protocol(self, protocol, host, port):
        try:
            self.sock.close()
        except:
            pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0))
        self.host = host
        self.port = port
        self.running = True
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()
