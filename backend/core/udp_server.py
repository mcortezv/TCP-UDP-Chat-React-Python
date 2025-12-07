import socket
import threading

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
        :param ip: direccion ip del servidor.
        :param port: puerto del servidor.
        :param controller: controla del servidor.
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
            # Establecer timeout para que el servidor pueda detenerse
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
                        continue

                    # Registrar cliente si no está registrado
                    if addr not in self.clients:
                        self.clients[addr] = f"unknown_{addr[1]}"
                        self.username_to_addr[self.clients[addr]] = addr

                    # Parsear el mensaje
                    if decoded.startswith("ALL:"):
                        # Mensaje broadcast
                        msg_content = decoded[4:]
                        print(f"[UDP Server] Broadcast: {msg_content}")

                        # SOLO los mensajes broadcast van al historial público
                        self.controller.history.append(msg_content)

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
                        print(f"[UDP Server] Partes del DM: {parts}")

                        if len(parts) >= 4:
                            recipient = parts[1]
                            sender_and_msg = ":".join(parts[2:])  # remitente: mensaje|timestamp

                            sender_username = self.clients.get(addr, 'unknown')
                            print(f"[UDP Server] DM de '{sender_username}' para '{recipient}'")
                            print(f"[UDP Server] Contenido: {sender_and_msg}")

                            # Guardar DM en una lista específica del usuario destinatario
                            dm_key = f"dm_{recipient}"
                            if dm_key not in self.controller.user_dms:
                                self.controller.user_dms[dm_key] = []
                            self.controller.user_dms[dm_key].append(sender_and_msg)
                            print(f"[UDP Server] ✓ DM guardado para {recipient}")

                            # También notificar al socket si está conectado (para UDP)
                            recipient_addr = self.username_to_addr.get(recipient)

                            if recipient_addr:
                                try:
                                    dm_msg = f"DM:{sender_and_msg}".encode()
                                    self.server.sendto(dm_msg, recipient_addr)
                                    print(f"[UDP Server] ✓ DM enviado exitosamente a {recipient} en {recipient_addr}")
                                except Exception as e:
                                    print(f"[UDP Server] ✗ Error enviando DM: {e}")
                                    self._remove_client(recipient_addr)

                            # Enviar confirmación al remitente
                            try:
                                confirm_msg = f"DM_SENT:{sender_and_msg}".encode()
                                self.server.sendto(confirm_msg, addr)
                                print(f"[UDP Server] ✓ Confirmación enviada al remitente")
                            except Exception as e:
                                print(f"[UDP Server] ✗ Error enviando confirmación: {e}")

                except Exception as e:
                    print(f"[UDP Server] Error decodificando: {e}")
                    continue

            except socket.timeout:
                # Timeout, es normal, continua el bucle
                continue
            except Exception as e:
                if self.running:
                    print(f"[UDP Server] Error: {e}")
                break

    def _remove_client(self, addr):
        """
        Funcion auxiliar para remover un cliente
        :param addr: dirección del cliente a remover
        """
        try:
            if addr in self.clients:
                username = self.clients[addr]
                del self.clients[addr]
                if username in self.username_to_addr:
                    del self.username_to_addr[username]
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