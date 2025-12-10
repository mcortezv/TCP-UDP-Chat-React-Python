import socket
import threading
import asyncio

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
        """
        try:
            decoded = message.decode()
            print(f"[TCP Server] Mensaje recibido: {decoded}")

            if decoded.startswith("ALL:"):
                # Mensaje broadcast - formato: ALL:username: mensaje|timestamp
                msg_content = decoded[4:]  # Remover "ALL:"
                parts = msg_content.split(":", 1)

                if len(parts) >= 2:
                    username = parts[0].strip()
                    rest = parts[1].strip()

                    # Dividir mensaje y timestamp
                    if "|" in rest:
                        text, timestamp_str = rest.rsplit("|", 1)
                        timestamp = float(timestamp_str)
                    else:
                        text = rest
                        timestamp = 0.0

                    # Añadir al historial estructurado
                    message_obj = self.controller.add_message_to_history(username, text, timestamp)

                    # Notificar por WebSocket
                    try:
                        from api.ws_server import notify_new_message
                        asyncio.run(notify_new_message(message_obj))
                    except:
                        pass

                    # Enviar a todos los sockets TCP excepto el remitente
                    for c in list(self.clients.keys()):
                        if c != source_sock:
                            try:
                                c.sendall(message)
                            except:
                                self._remove_client(c)

            elif decoded.startswith("DM:"):
                # Mensaje directo - formato: DM:destinatario:remitente: mensaje|timestamp
                parts = decoded.split(":", 3)

                if len(parts) >= 4:
                    recipient = parts[1]
                    sender = parts[2]
                    rest = parts[3].strip()

                    # Dividir mensaje y timestamp
                    if "|" in rest:
                        text, timestamp_str = rest.rsplit("|", 1)
                        timestamp = float(timestamp_str)
                    else:
                        text = rest
                        timestamp = 0.0

                    print(f"[TCP Server] DM de '{sender}' para '{recipient}': {text}")

                    # Guardar DM estructurado
                    dm_obj = self.controller.add_dm_to_user(recipient, sender, text, timestamp)

                    # Notificar por WebSocket
                    try:
                        from api.ws_server import notify_dm
                        asyncio.run(notify_dm(sender, recipient, dm_obj))
                    except:
                        pass

                    # Enviar al socket TCP del destinatario si está conectado
                    recipient_sock = None
                    for sock, username in self.clients.items():
                        if username == recipient:
                            recipient_sock = sock
                            break

                    if recipient_sock:
                        try:
                            dm_msg = f"DM:{sender}: {text}|{timestamp}".encode()
                            recipient_sock.sendall(dm_msg)
                            print(f"[TCP Server] DM enviado a socket de {recipient}")
                        except Exception as e:
                            print(f"[TCP Server] Error enviando DM: {e}")
                            self._remove_client(recipient_sock)

                    # Confirmar al remitente
                    try:
                        confirm_msg = f"DM_SENT:{sender}: {text}|{timestamp}".encode()
                        source_sock.sendall(confirm_msg)
                    except Exception as e:
                        print(f"[TCP Server] Error enviando confirmación: {e}")

        except Exception as e:
            print(f"[TCP Server] Error en broadcast: {e}")

    def _remove_client(self, conn):
        """
        Funcion auxiliar para remover un cliente
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
        """
        username = None

        while self.running:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                decoded = data.decode()

                if decoded.startswith("CONECTADO:"):
                    username = decoded.split(":", 1)[1]
                    self.clients[conn] = username
                    print(f"[TCP Server] Usuario {username} conectado")

                    # Notificar actualización de clientes
                    try:
                        from api.ws_server import manager
                        asyncio.run(manager.send_clients_update())
                    except:
                        pass
                    continue

                self.broadcast(data, conn)

            except Exception as e:
                print(f"[TCP Server] Error manejando cliente: {e}")
                break

        self._remove_client(conn)
        if username:
            print(f"[TCP Server] Usuario {username} desconectado")
            # Notificar actualización de clientes
            try:
                from api.ws_server import manager
                asyncio.run(manager.send_clients_update())
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
        for c in list(self.clients.keys()):
            try:
                c.close()
            except:
                pass
        self.clients.clear()