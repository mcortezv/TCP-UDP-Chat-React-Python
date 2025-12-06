import socket
import threading

"""
Modulo que reprsenta un servidor TCP
"""

class TCPServer(threading.Thread):
    """
    Clase que representa un servidor TCP, permite crearlo correrlo y detenerlo.
    """
    def __init__(self, ip, port, controller):
        """
        Constructor de la clase.
        :param ip: direccion ip del servidor.
        :param port: puerto del servidor.
        :param controller: controla del servidor.
        """
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.controller = controller
        self.clients = set()
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))
        self.server.listen()

    def run(self):
        """
        Funcion que permite correr el servidor.
        """
        while self.running:
            try:
                conn, addr = self.server.accept()
            except:
                break
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def broadcast(self, message, source_sock):
        """
        Funcion que envia un mensaje a todos los clientes conectados.
        :param message: mensaje a enviar.
        :param source_sock: socket del emisor.
        :return:
        """
        try:
            decoded = message.decode()
            self.controller.history.append(decoded)
        except:
            pass
        for c in list(self.clients):
            if c != source_sock:
                try:
                    c.sendall(message)
                except:
                    try:
                        self.clients.remove(c)
                        c.close()
                    except:
                        pass

    def handle_client(self, conn, addr):
        """
        Manejador del cliente dentro de la conexion al servidor.
        :param conn: socket que representa la conexion al servidor.
        :param addr: direccion ip del cliente.
        """
        self.clients.add(conn)
        while self.running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                self.broadcast(data, conn)
            except:
                break
        try:
            self.clients.remove(conn)
        except:
            pass
        try:
            conn.close()
        except:
            pass


    def stop(self):
        """
        Funcion que permite detener el servidor.
        """
        self.running = False
        try:
            self.server.close()
        except:
            pass
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.port))
            s.close()
        except:
            pass
        for c in list(self.clients):
            try:
                c.close()
            except:
                pass
        self.clients.clear()
