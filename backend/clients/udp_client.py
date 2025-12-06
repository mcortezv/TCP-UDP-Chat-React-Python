import socket
import threading
import time


class UDPClient:
    def __init__(self, username, host, port, controller):
        self.username = username
        self.host = host
        self.port = port
        self.controller = controller
        self.sock = None
        self.running = True
        self.recv_thread = None

    def start(self):
        try:
            # Crear socket UDP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Bind para poder recibir mensajes
            self.sock.bind(("", 0))
            local_port = self.sock.getsockname()[1]



            # Iniciar hilo de recepción
            self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self.recv_thread.start()
        except Exception as e:
            pass

    def _recv_loop(self):
        if not self.sock:
            return

        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                # Los mensajes ya estan en el historial del servidor
            except Exception as e:
                break

    def send(self, message: str):
        if not self.sock:
            return False

        payload = f"{self.username}: {message}|{time.time()}".encode()
        try:
            self.sock.sendto(payload, (self.host, self.port))
            return True
        except Exception as e:
            return False

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass