from core.tcp_server import TCPServer
from core.udp_server import UDPServer
from clients.tcp_client import TCPClient
from clients.udp_client import UDPClient
import threading

"""
Modulo controlador del servidor
"""


class ServerController:
    """
    Clase que representa el controlador del servidor
    Permite configurarlo y ejecutarlo
    """

    def __init__(self):
        """
        Constructor del controlador del servidor
        Settea el servidor en None y configura protocolo ip y puerto
        La lista de clientes evita duplicados y mantiene el limite
        Tiene historial de mensajes y diccionario de sockets
        """
        self.server = None
        self.protocol = None
        self.HOST = "0.0.0.0"
        self.PORT = 1060
        self.clients = set()
        self.client_objs = {}
        self.history = []
        self.user_dms = {}  # Diccionario para almacenar DMs por usuario: {dm_username: [mensajes]}
        self._lock = threading.RLock()

    def run(self, protocol: str):
        """
        Funcion que ejecuta el servidor segun el protocolo
        :param protocol: protocolo del servidor (tcp o udp)
        """
        with self._lock:
            if self.server is not None:
                return {"error": "Servidor ya corriendo. Deten el servidor primero."}
            try:
                if protocol == "tcp":
                    self.server = TCPServer(self.HOST, self.PORT, self)
                elif protocol == "udp":
                    self.server = UDPServer(self.HOST, self.PORT, self)
                else:
                    return {"error": "Protocolo invalido"}
                self.protocol = protocol
                self.server.start()

                # Verificar que el servidor realmente inicio
                import time
                time.sleep(0.5)
                if not self.server.running:
                    error_msg = f"El servidor {protocol.upper()} no pudo iniciar correctamente"
                    self.server = None
                    self.protocol = None
                    return {"error": error_msg}
                return {"status": f"Servidor {protocol} iniciado"}
            except Exception as e:
                self.server = None
                self.protocol = None
                return {"error": f"Error al iniciar servidor: {str(e)}"}

    def shutdown(self):
        """
        Funcion que detiene el servidor
        """
        with self._lock:
            if not self.server:
                return {"status": "No hay servidor corriendo"}
            # Detener y desconectar todos los clientes
            for username, cli in list(self.client_objs.items()):
                try:
                    cli.stop()
                except Exception as e:
                    pass
            self.client_objs.clear()
            self.clients.clear()
            # Detener el servidor
            try:
                self.server.stop()
                if hasattr(self.server, 'join'):
                    self.server.join(timeout=2)
            except Exception as e:
                pass
            self.server = None
            self.protocol = None
            return {"status": "Servidor detenido"}

    def is_running(self):
        """
        Funcion que permite validar si el servidor esta corriendo
        """
        return self.server is not None

    def create_client(self, username: str):
        """
        Funcion que permite crear un cliente en el servidor
        Verifica el limite maximo de 5 conexiones
        :param username: nombre del usuario
        """
        with self._lock:
            if not self.is_running():
                raise ValueError("El servidor no esta corriendo")
            if username in self.clients:
                raise ValueError("El usuario ya esta conectado")
            if len(self.clients) >= 5:
                raise ValueError("Limite de 5 conexiones alcanzado")
            
            self.clients.add(username)

            # Crear cliente segun el protocolo actual
            if self.protocol == "tcp":
                client = TCPClient(username, self.HOST, self.PORT, self)
            elif self.protocol == "udp":
                client = UDPClient(username, self.HOST, self.PORT, self)
            else:
                return None
            self.client_objs[username] = client
            client.start()

            # Dar tiempo para que se conecte y se complete el handshake RSA
            import time
            time.sleep(0.5)
            return client

    def remove_client(self, username: str):
        """
        Funcion que permite eliminar un cliente
        de la lista de clientes y sockets del servidor
        :param username: nombre del usuario
        """
        with self._lock:
            if username in self.client_objs:
                try:
                    self.client_objs[username].stop()
                except Exception as e:
                    pass
                del self.client_objs[username]
            if username in self.clients:
                self.clients.remove(username)

    def add_message_to_history(self, username: str, text: str, timestamp: float):
        """
        Anade un mensaje broadcast al historial
        :param username: usuario que envio el mensaje
        :param text: contenido del mensaje
        :param timestamp: timestamp del mensaje
        :return: objeto del mensaje para notificaciones
        """
        message_obj = {
            "user": username,
            "text": text,
            "timestamp": timestamp,
            "isDM": False
        }

        with self._lock:
            self.history.append(message_obj)

        print(f"[Controller] Mensaje agregado al historial: {username}: {text}")
        return message_obj

    def add_dm_to_user(self, recipient: str, sender: str, text: str, timestamp: float):
        """
        Anade un mensaje privado al buzon del usuario destinatario
        :param recipient: usuario destinatario
        :param sender: usuario remitente
        :param text: contenido del mensaje
        :param timestamp: timestamp del mensaje
        :return: objeto del mensaje para notificaciones
        """
        dm_obj = {
            "user": sender,
            "text": text,
            "timestamp": timestamp,
            "isDM": True,
            "dmRecipient": recipient
        }

        dm_key = f"dm_{recipient}"

        with self._lock:
            if dm_key not in self.user_dms:
                self.user_dms[dm_key] = []
            self.user_dms[dm_key].append(dm_obj)

        print(f"[Controller] DM guardado para {recipient}: {sender} -> {text}")
        return dm_obj

    def get_chat_history(self):
        """
        Obtiene el historial completo de mensajes broadcast
        :return: lista de mensajes
        """
        with self._lock:
            return self.history.copy()

    def get_user_dms(self, username: str):
        """
        Obtiene y limpia los mensajes privados de un usuario
        :param username: nombre del usuario
        :return: lista de mensajes privados
        """
        dm_key = f"dm_{username}"
        with self._lock:
            dms = self.user_dms.get(dm_key, []).copy()
            if dm_key in self.user_dms:
                self.user_dms[dm_key].clear()
        return dms