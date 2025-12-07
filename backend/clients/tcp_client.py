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
        self.dm_queue = []  # Cola de DMs recibidos

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

                decoded = data.decode()
                print(f"[TCP Client {self.username}] Mensaje recibido: {decoded}")

                # Procesar mensajes DM recibidos
                if decoded.startswith("DM:") or decoded.startswith("DM_SENT:"):
                    # Este es un DM, el frontend lo manejará via WebSocket o polling
                    # Por ahora solo lo logueamos
                    print(f"[TCP Client {self.username}] DM procesado")

            except Exception as e:
                print(f"[TCP Client {self.username}] Error recibiendo: {e}")
                break
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.sock = None

    def send(self, message: str, recipient: str = "all"):
        """
        Funcion que permite enviar mensajes en el servidor
        :param message: mensaje que se envia
        :param recipient: destinatario del mensaje ("all" para broadcast)
        :return: True si se envió correctamente, False en caso contrario
        """
        if not self.sock:
            print(f"[TCP Client] Error: Socket no disponible")
            return False

        try:
            # Formato: DESTINATARIO:REMITENTE: mensaje|timestamp
            if recipient == "all":
                payload = f"ALL:{self.username}: {message}|{time.time()}".encode()
            else:
                payload = f"DM:{recipient}:{self.username}: {message}|{time.time()}".encode()

            self.sock.sendall(payload)
            return True
        except Exception as e:
            print(f"[TCP Client] Error enviando mensaje: {e}")
            self.sock = None
            return False

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