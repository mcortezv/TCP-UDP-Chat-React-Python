import socket
import threading
import time


class UDPClient:
    """
    Clase que represta un objeto tipo Cliente UDP, permite recibir y enviar mensajes.
    """
    def __init__(self, username, host, port, controller):
        """
        Constructor de la clase UDPClient
        :param username: nombre del usuario de la conexion
        :param host: direcccion ip del servidor
        :param port: puerto del servidor
        :param controller: controlador del cliente
        """
        self.username = username
        self.host = host
        self.port = port
        self.controller = controller
        self.sock = None
        self.running = True
        self.recv_thread = None

    def start(self):
        """
        Funcion que permite iniciar el hilo del cliente
        """
        try:
            # Crear socket UDP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Bind para poder recibir mensajes
            self.sock.bind(("", 0))
            local_port = self.sock.getsockname()[1]
            # Iniciar hilo de recepcion
            self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self.recv_thread.start()
        except Exception as e:
            pass

    def _recv_loop(self):
        """
        Funcion que crea un bucle de recepcion de mensajes
        """
        if not self.sock:
            return
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                # Los mensajes ya estan en el historial del servidor
            except Exception as e:
                break

    def send(self, message: str):
        """
        Funcion que permite enviar mensajes en el servidor
        :param message: mensaje que se envia
        """
        if not self.sock:
            return False

        payload = f"{self.username}: {message}|{time.time()}".encode()
        try:
            self.sock.sendto(payload, (self.host, self.port))
            return True
        except Exception as e:
            return False

    def stop(self):
        """
        Funcion que permite cerrar el socket del cliente
        """
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
