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
        self.dm_queue = []  # Cola de DMs recibidos

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
                decoded = data.decode()
                print(f"[UDP Client {self.username}] Mensaje recibido: {decoded}")

                # Procesar mensajes DM recibidos
                if decoded.startswith("DM:"):
                    # Formato: DM:remitente: mensaje|timestamp
                    msg_content = decoded[3:]  # Remover "DM:"
                    self.dm_queue.append(msg_content)
                    print(f"[UDP Client {self.username}] DM agregado a cola: {msg_content}")
                elif decoded.startswith("DM_SENT:"):
                    # Confirmación de DM enviado, ignorar
                    print(f"[UDP Client {self.username}] Confirmación de DM enviado")
                    pass

            except Exception as e:
                print(f"[UDP Client {self.username}] Error recibiendo: {e}")
                break

    def get_dms(self):
        """
        Obtiene y limpia la cola de DMs recibidos
        :return: lista de DMs
        """
        dms = self.dm_queue.copy()
        self.dm_queue.clear()
        return dms

    def send(self, message: str, recipient: str = "all"):
        """
        Funcion que permite enviar mensajes en el servidor
        :param message: mensaje que se envia
        :param recipient: destinatario del mensaje ("all" para broadcast)
        :return: True si se envió correctamente, False en caso contrario
        """
        if not self.sock:
            print(f"[UDP Client] Error: Socket no disponible")
            return False

        try:
            if recipient == "all":
                payload = f"ALL:{self.username}: {message}|{time.time()}".encode()
            else:
                payload = f"DM:{recipient}:{self.username}: {message}|{time.time()}".encode()

            self.sock.sendto(payload, (self.host, self.port))
            return True
        except Exception as e:
            print(f"[UDP Client] Error enviando mensaje: {e}")
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