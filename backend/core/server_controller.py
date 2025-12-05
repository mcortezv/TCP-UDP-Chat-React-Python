from core.tcp_server import TCPServer
from core.udp_server import UDPServer
from clients.tcp_client import TCPClient
from clients.udp_client import UDPClient
import threading


class ServerController:
    def __init__(self):
        self.server = None
        self.protocol = None
        self.HOST = "192.168.0.3"
        self.PORT = 1060

        self.clients = set()
        self.client_objs = {}
        self.history = []
        self._lock = threading.RLock()


    def run(self, protocol: str):
        with self._lock:
            if self.server is not None:
                return {"error": "Servidor ya corriendo", "protocol": self.protocol}
            if protocol == "tcp":
                self.server = TCPServer(self.HOST, self.PORT, self)
            elif protocol == "udp":
                self.server = UDPServer(self.HOST, self.PORT, self)
            else:
                return {"error": "Protocolo inválido"}
            self.protocol = protocol
            self.server.start()
            for username, cli in list(self.client_objs.items()):
                cli.switch_protocol(protocol, self.HOST, self.PORT)
            return {"status": f"Servidor {protocol} iniciado"}


    def shutdown(self):
        with self._lock:
            if not self.server:
                return {"status": "No hay servidor corriendo"}

            try:
                self.server.stop()
            except:
                pass

            self.server = None
            self.protocol = None

            return {"status": "Servidor detenido"}


    def switch_protocol(self, new_protocol: str):
        with self._lock:
            old = self.protocol
        if old is not None:
            try:
                self.server.stop()
            except:
                pass
        with self._lock:
            self.server = None
            self.protocol = None
        return self.run(new_protocol)


    def is_running(self):
        return self.server is not None


    def create_client(self, username: str):
        with self._lock:
            if username in self.clients:
                return None
            self.clients.add(username)
            if self.protocol == "tcp":
                cli = TCPClient(username, self.HOST, self.PORT, self)
            elif self.protocol == "udp":
                cli = UDPClient(username, self.HOST, self.PORT, self)
            else:
                cli = TCPClient(username, self.HOST, self.PORT, self)

            self.client_objs[username] = cli
            cli.start()
            return cli


    def remove_client(self, username: str):
        with self._lock:
            if username in self.client_objs:
                try:
                    self.client_objs[username].stop()
                except:
                    pass
                del self.client_objs[username]

            if username in self.clients:
                self.clients.remove(username)
