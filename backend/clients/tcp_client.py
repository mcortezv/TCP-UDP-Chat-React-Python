import socket
import threading
import time


class TCPClient:
    def __init__(self, username, host, port, controller):
        self.username = username
        self.host = host
        self.port = port
        self.controller = controller
        self.sock = None
        self.running = True
        self.recv_thread = None
        self.connect_lock = threading.Lock()

    def start(self):
        threading.Thread(target=self._connect_loop, daemon=True).start()

    def _connect_loop(self):
        while self.running:
            if self.sock is None:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.host, self.port))
                    self.sock = s
                    self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                    self.recv_thread.start()
                except:
                    self.sock = None
            time.sleep(1)

    def _recv_loop(self):
        while self.running and self.sock:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
            except:
                break
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.sock = None

    def send(self, message: str):
        payload = f"{self.username}: {message}|{time.time()}".encode()
        if self.sock:
            try:
                self.sock.sendall(payload)
            except:
                pass

    def stop(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except:
            pass

    def switch_protocol(self, protocol, host, port):
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.sock = None
        self.host = host
        self.port = port
