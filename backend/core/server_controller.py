from core.tcp_server import TCPServer
from core.udp_server import UDPServer
from clients.tcp_client import TCPClient
from clients.udp_client import UDPClient
import threading


class ServerController:
    def __init__(self):
        self.server = None
        self.protocol = None
        self.HOST = "127.0.0.1"
        self.PORT = 1060

        self.clients = set()
        self.client_objs = {}
        self.history = []
        self._lock = threading.RLock()

    def run(self, protocol: str):
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
                    print(f"[Controller] ERROR: {error_msg}")
                    self.server = None
                    self.protocol = None
                    return {"error": error_msg}
                return {"status": f"Servidor {protocol} iniciado"}
            except Exception as e:
                self.server = None
                self.protocol = None
                return {"error": f"Error al iniciar servidor: {str(e)}"}

    def shutdown(self):
        with self._lock:
            if not self.server:
                return {"status": "No hay servidor corriendo"}
            # Detener y desconectar todos los clientes
            for username, cli in list(self.client_objs.items()):
                try:
                    cli.stop()
                except Exception as e:
                    print(f"[Controller] Error deteniendo cliente {username}: {e}")
            self.client_objs.clear()
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
        return self.server is not None

    def create_client(self, username: str):
        with self._lock:
            if username in self.clients:
                print(f"[Controller] Cliente {username} ya existe")
                return None
            if not self.is_running():
                print(f"[Controller] No hay servidor corriendo")
                return None
            self.clients.add(username)

            # Crear cliente según el protocolo actual
            if self.protocol == "tcp":
                cli = TCPClient(username, self.HOST, self.PORT, self)
            elif self.protocol == "udp":
                cli = UDPClient(username, self.HOST, self.PORT, self)
            else:
                return None
            self.client_objs[username] = cli
            cli.start()

            # Dar tiempo para que se conecte (solo TCP)
            if self.protocol == "tcp":
                import time
                time.sleep(0.5)
            return cli

    def remove_client(self, username: str):
        with self._lock:
            if username in self.client_objs:
                try:
                    self.client_objs[username].stop()
                except Exception as e:
                    pass
                del self.client_objs[username]
            if username in self.clients:
                self.clients.remove(username)