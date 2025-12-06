import socket
import threading
import time


class TCPClient:
    """
    Clase que represta un objeto tipo Cliente TCP, permite iniciar
    una conexión, recibir y enviar mensajes.
    """
    def __init__(self, username, host, port, controller):
        """
        Contructor de la clase TCPClient
        :param username: nombre del usuario de la conexion
        :param host: direccion ip del servidor
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
        self.connect_lock = threading.Lock()

    def start(self):
        """
        Funcion que permite iniciar el hilo del cliente
        """
        threading.Thread(target=self._connect_loop, daemon=True).start()

    def _connect_loop(self):
        """
        Funcion que crea un bucle de conexion con el servidor
        """
        while self.running:
            if self.sock is None:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((self.host, self.port))
                    s.settimeout(None)

                    # Registrar usuario en el servidor
                    register_msg = f"CONECTADO:{self.username}".encode()
                    s.sendall(register_msg)

                    self.sock = s
                    self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                    self.recv_thread.start()
                except Exception as e:
                    self.sock = None
            time.sleep(1)

    def _recv_loop(self):
        """
        Funcion que crea un bucle de recepcion de mensajes
        """
        while self.running and self.sock:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                # Los mensajes ya estan en el historial del servidor
            except Exception as e:
                break
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.sock = None

    def send(self, message: str):
        """
        Funcion que permite enviar mensajes en el servidor
        :param message: mensaje que se envia
        """
        payload = f"{self.username}: {message}|{time.time()}".encode()
        if self.sock:
            try:
                self.sock.sendall(payload)
            except Exception as e:
                self.sock = None

    def stop(self):
        """
        Funcion que permite cerrar el socket del cliente
        """
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
