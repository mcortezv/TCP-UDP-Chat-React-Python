from core.tcp_server import TCPServer
from core.udp_server import UDPServer

class ProtocolSelector:

    def __init__(self):
        self.server = None
        self.HOST = "192.168.0.3"
        self.PORT = 1060

        self.clients = set()
        self.history = []

    def run(self, protocol):
        if protocol == 'tcp':
            self.server = TCPServer(self.HOST, self.PORT, self.clients)
        elif protocol == 'udp':
            self.server = UDPServer(self.HOST, self.PORT, self.clients)
        else:
            return {"error": "Protocolo inválido"}

        self.server.start()
        return {"status": f"Servidor {protocol} iniciado"}

    def shutdown(self):
        if self.server:
            self.server.shutdown()
