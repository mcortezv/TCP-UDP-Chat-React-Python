import socket
import threading
import asyncio

"""
Modulo que reprsenta un servidor UDP
"""


class UDPServer(threading.Thread):
    """
    Clase que representa un servidor UDP, permite crearlo correrlo y detenerlo.
    """

    def __init__(self, ip, port, controller):
        """
        Constructor de la clase.
        """
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.controller = controller
        self.server = None
        self.running = False
        self.clients = {}  # addr -> username
        self.username_to_addr = {}  # username -> addr (índice inverso)
        self.init_error = None
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((ip, port))
            self.running = True
        except Exception as e:
            self.init_error = str(e)
            self.running = False
            if self.server:
                try:
                    self.server.close()
                except:
                    pass
                self.server = None

    def run(self):
        """
        Funcion que permite correr el servidor.
        """
        if not self.running or not self.server:
            return
        try:
            self.server.settimeout(1.0)
        except Exception as e:
            self.running = False
            return

        while self.running:
            try:
                data, addr = self.server.recvfrom(1024)
                try:
                    decoded = data.decode()

                    # Manejar registro
                    if decoded.startswith("Conectado:"):
                        username = decoded.split(":", 1)[1]
                        self.clients[addr] = username
                        self.username_to_addr[username] = addr
                        print(f"[UDP Server] Usuario {username} conectado desde {addr}")

                        # Notificar actualización de clientes
                        try:
                            from api.ws_server import manager
                            asyncio.run(manager.send_clients_update())
                        except:
                            pass
                        continue

                    # Registrar cliente si no está registrado
                    if addr not in self.clients:
                        self.clients[addr] = f"unknown_{addr[1]}"
                        self.username_to_addr[self.clients[addr]] = addr

                    # Parsear el mensaje
                    if decoded.startswith("ALL:"):
                        # Mensaje broadcast
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

                            print(f"[UDP Server] Broadcast de {username}: {text}")

                            # Añadir al historial estructurado
                            message_obj = self.controller.add_message_to_history(username, text, timestamp)

                            # Notificar por WebSocket
                            try:
                                from api.ws_server import notify_new_message
                                asyncio.run(notify_new_message(message_obj))
                            except:
                                pass

                            # Broadcast a todos menos al remitente
                            for client_addr in list(self.clients.keys()):
                                if client_addr != addr:
                                    try:
                                        self.server.sendto(data, client_addr)
                                    except Exception as e:
                                        self._remove_client(client_addr)

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

                            print(f"[UDP Server] DM de '{sender}' para '{recipient}': {text}")

                            # Guardar DM estructurado
                            dm_obj = self.controller.add_dm_to_user(recipient, sender, text, timestamp)

                            # Notificar por WebSocket
                            try:
                                from api.ws_server import notify_dm
                                asyncio.run(notify_dm(sender, recipient, dm_obj))
                            except:
                                pass

                            # Enviar al destinatario UDP si está conectado
                            recipient_addr = self.username_to_addr.get(recipient)

                            if recipient_addr:
                                try:
                                    dm_msg = f"DM:{sender}: {text}|{timestamp}".encode()
                                    self.server.sendto(dm_msg, recipient_addr)
                                    print(f"[UDP Server] DM enviado a {recipient} en {recipient_addr}")
                                except Exception as e:
                                    print(f"[UDP Server] Error enviando DM: {e}")
                                    self._remove_client(recipient_addr)

                            # Enviar confirmación al remitente
                            try:
                                confirm_msg = f"DM_SENT:{sender}: {text}|{timestamp}".encode()
                                self.server.sendto(confirm_msg, addr)
                                print(f"[UDP Server] Confirmación enviada al remitente")
                            except Exception as e:
                                print(f"[UDP Server] Error enviando confirmación: {e}")

                except Exception as e:
                    print(f"[UDP Server] Error decodificando: {e}")
                    continue

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[UDP Server] Error: {e}")
                break

    def _remove_client(self, addr):
        """
        Funcion auxiliar para remover un cliente
        """
        try:
            if addr in self.clients:
                username = self.clients[addr]
                del self.clients[addr]
                if username in self.username_to_addr:
                    del self.username_to_addr[username]

                # Notificar actualización de clientes
                try:
                    from api.ws_server import manager
                    asyncio.run(manager.send_clients_update())
                except:
                    pass
        except:
            pass

    def stop(self):
        """
        Funcion que permite detener el servidor.
        """
        self.running = False
        self.clients.clear()
        self.username_to_addr.clear()
        if self.server:
            try:
                self.server.close()
            except Exception as e:
                pass