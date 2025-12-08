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
        self.clients = {}  # socket -> username
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
        """
        try:
            decoded = message.decode()
            print(f"[TCP Server] Mensaje recibido: {decoded}")

            # Parsear el mensaje para determinar el tipo
            if decoded.startswith("ALL:"):
                # Mensaje broadcast - formato: ALL:username: mensaje|timestamp
                msg_content = decoded[4:]  # Remover "ALL:"
                print(f"[TCP Server] Broadcast: {msg_content}")

                # SOLO los mensajes broadcast van al historial público
                self.controller.history.append(msg_content)

                # Enviar a todos excepto el remitente
                for c in list(self.clients.keys()):
                    if c != source_sock:
                        try:
                            c.sendall(message)
                        except:
                            self._remove_client(c)

            elif decoded.startswith("DM:"):
                # Mensaje directo - formato: DM:destinatario:remitente: mensaje|timestamp
                parts = decoded.split(":", 3)
                print(f"[TCP Server] Partes del DM: {parts}")

                if len(parts) >= 4:
                    recipient = parts[1]
                    sender_and_msg = ":".join(parts[2:])  # remitente: mensaje|timestamp

                    sender_username = self.clients.get(source_sock, 'unknown')
                    print(f"[TCP Server] DM de '{sender_username}' para '{recipient}'")
                    print(f"[TCP Server] Contenido: {sender_and_msg}")

                    # Guardar DM en una lista específica del usuario destinatario
                    dm_key = f"dm_{recipient}"
                    if dm_key not in self.controller.user_dms:
                        self.controller.user_dms[dm_key] = []
                    self.controller.user_dms[dm_key].append(sender_and_msg)
                    print(f"[TCP Server] DM guardado para {recipient}")

                    # También notificar al socket si está conectado (para TCP)
                    recipient_sock = None
                    for sock, username in self.clients.items():
                        if username == recipient:
                            recipient_sock = sock
                            print(f"[TCP Server] Destinatario encontrado!")
                            break

                    if recipient_sock:
                        try:
                            dm_msg = f"DM:{sender_and_msg}".encode()
                            recipient_sock.sendall(dm_msg)
                            print(f"[TCP Server] DM enviado exitosamente a socket de {recipient}")
                        except Exception as e:
                            print(f"[TCP Server] Error enviando DM a socket: {e}")
                            self._remove_client(recipient_sock)

                    # Enviar confirmación al remitente
                    try:
                        confirm_msg = f"DM_SENT:{sender_and_msg}".encode()
                        source_sock.sendall(confirm_msg)
                        print(f"[TCP Server] Confirmación enviada al remitente")
                    except Exception as e:
                        print(f"[TCP Server] Error enviando confirmación: {e}")
        except Exception as e:
            print(f"[TCP Server] Error en broadcast: {e}")

    def _remove_client(self, conn):
        """
        Funcion auxiliar para remover un cliente
        :param conn: socket del cliente a remover
        """
        try:
            if conn in self.clients:
                del self.clients[conn]
            conn.close()
        except:
            pass

    def handle_client(self, conn, addr):
        """
        Manejador del cliente dentro de la conexion al servidor.
        :param conn: socket que representa la conexion al servidor.
        :param addr: direccion ip del cliente.
        """
        username = None

        while self.running:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                decoded = data.decode()

                # Manejar registro de usuario
                if decoded.startswith("CONECTADO:"):
                    username = decoded.split(":", 1)[1]
                    self.clients[conn] = username
                    print(f"[TCP Server] Usuario {username} conectado")
                    continue

                # Procesar mensaje normal
                self.broadcast(data, conn)

            except Exception as e:
                print(f"[TCP Server] Error manejando cliente: {e}")
                break

        # Limpiar al desconectar
        self._remove_client(conn)
        if username:
            print(f"[TCP Server] Usuario {username} desconectado")

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
        for c in list(self.clients.keys()):
            try:
                c.close()
            except:
                pass
        self.clients.clear()