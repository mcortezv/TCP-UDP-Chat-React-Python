import socket
import threading
import asyncio
from core.crypto import generate_keys, export_pubkey, import_pubkey, encrypt_text, decrypt_text

"""
Modulo que reprsenta un servidor TCP
"""


class TCPServer(threading.Thread):
    """
    Clase que representa un servidor TCP, permite crearlo correrlo y detenerlo
    """

    def __init__(self, ip, port, controller):
        """
        Constructor de la clase
        """
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.controller = controller
        self.clients = {}  # socket -> username
        self.client_pubkeys = {}  # username -> pubkey
        self.running = True
        # Generar par de claves del servidor
        self.pubkey, self.privkey = generate_keys()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))
        self.server.listen()

    def run(self):
        """
        Funcion que permite correr el servidor
        """
        while self.running:
            try:
                conn, addr = self.server.accept()
            except:
                break
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def broadcast(self, message, source_sock):
        """
        Funcion que envia un mensaje a todos los clientes conectados
        El mensaje viene con el texto cifrado, se descifra y se re-cifra
        con la clave publica de cada destinatario
        """
        try:
            decoded = message.decode()
            print(f"[TCP Server] Mensaje recibido: {decoded}")

            if decoded.startswith("ALL:"):
                # Mensaje broadcast - formato: ALL:username: <cifrado>|timestamp
                msg_content = decoded[4:]  # Remover "ALL:"
                parts = msg_content.split(":", 1)

                if len(parts) >= 2:
                    username = parts[0].strip()
                    rest = parts[1].strip()

                    # Dividir mensaje cifrado y timestamp
                    if "|" in rest:
                        cifrado, timestamp_str = rest.rsplit("|", 1)
                        timestamp = float(timestamp_str)
                    else:
                        cifrado = rest
                        timestamp = 0.0

                    # Descifrar el texto con la clave privada del servidor
                    text = decrypt_text(cifrado, self.privkey)

                    # Añadir al historial estructurado (en texto plano)
                    message_obj = self.controller.add_message_to_history(username, text, timestamp)

                    # Notificar por WebSocket
                    try:
                        from api.ws_server import notify_new_message
                        asyncio.run(notify_new_message(message_obj))
                    except:
                        pass

                    # Reenviar a cada cliente conectado, cifrado con su clave publica
                    for c, dest_user in list(self.clients.items()):
                        if c == source_sock:
                            continue
                        dest_pubkey = self.client_pubkeys.get(dest_user)
                        if not dest_pubkey:
                            continue
                        try:
                            cifrado_dest = encrypt_text(text, dest_pubkey)
                            payload = f"ALL:{username}: {cifrado_dest}|{timestamp}".encode()
                            c.sendall(payload)
                        except:
                            self._remove_client(c)

            elif decoded.startswith("DM:"):
                # Mensaje directo - formato: DM:destinatario:remitente: <cifrado>|timestamp
                parts = decoded.split(":", 3)

                if len(parts) >= 4:
                    recipient = parts[1]
                    sender = parts[2]
                    rest = parts[3].strip()

                    # Dividir mensaje cifrado y timestamp
                    if "|" in rest:
                        cifrado, timestamp_str = rest.rsplit("|", 1)
                        timestamp = float(timestamp_str)
                    else:
                        cifrado = rest
                        timestamp = 0.0

                    # Descifrar texto
                    text = decrypt_text(cifrado, self.privkey)

                    print(f"[TCP Server] DM de '{sender}' para '{recipient}': {text}")

                    # Guardar DM estructurado (en texto plano)
                    dm_obj = self.controller.add_dm_to_user(recipient, sender, text, timestamp)

                    # Notificar por WebSocket
                    try:
                        from api.ws_server import notify_dm
                        asyncio.run(notify_dm(sender, recipient, dm_obj))
                    except:
                        pass

                    # Buscar el socket del destinatario y enviarle el mensaje cifrado con su clave
                    recipient_sock = None
                    for sock, username in self.clients.items():
                        if username == recipient:
                            recipient_sock = sock
                            break

                    if recipient_sock:
                        dest_pubkey = self.client_pubkeys.get(recipient)
                        if dest_pubkey:
                            try:
                                cifrado_dest = encrypt_text(text, dest_pubkey)
                                dm_msg = f"DM:{sender}: {cifrado_dest}|{timestamp}".encode()
                                recipient_sock.sendall(dm_msg)
                                print(f"[TCP Server] DM enviado a socket de {recipient}")
                            except Exception as e:
                                print(f"[TCP Server] Error enviando DM: {e}")
                                self._remove_client(recipient_sock)

                    # Confirmar al remitente con su mismo texto cifrado para el (su pubkey)
                    sender_pubkey = self.client_pubkeys.get(sender)
                    if sender_pubkey:
                        try:
                            cifrado_sender = encrypt_text(text, sender_pubkey)
                            confirm_msg = f"DM_SENT:{sender}: {cifrado_sender}|{timestamp}".encode()
                            source_sock.sendall(confirm_msg)
                        except Exception as e:
                            print(f"[TCP Server] Error enviando confirmacion: {e}")

        except Exception as e:
            print(f"[TCP Server] Error en broadcast: {e}")

    def _remove_client(self, conn):
        """
        Funcion auxiliar para remover un cliente
        """
        try:
            if conn in self.clients:
                username = self.clients[conn]
                if username in self.client_pubkeys:
                    del self.client_pubkeys[username]
                del self.clients[conn]
            conn.close()
        except:
            pass

    def handle_client(self, conn, addr):
        """
        Manejador del cliente dentro de la conexion al servidor
        """
        username = None

        while self.running:
            try:
                data = conn.recv(4096)
                if not data:
                    break

                decoded = data.decode()

                if decoded.startswith("CONECTADO:"):
                    # Formato: CONECTADO:username|<pubkey_b64>
                    payload = decoded.split(":", 1)[1]
                    if "|" in payload:
                        username, pubkey_b64 = payload.split("|", 1)
                        try:
                            client_pub = import_pubkey(pubkey_b64)
                            self.client_pubkeys[username] = client_pub
                        except Exception as e:
                            print(f"[TCP Server] Error importando pubkey de {username}: {e}")
                    else:
                        username = payload

                    self.clients[conn] = username
                    print(f"[TCP Server] Usuario {username} conectado")

                    # Enviar la clave publica del servidor al cliente
                    try:
                        server_pub_b64 = export_pubkey(self.pubkey)
                        conn.sendall(f"PUBKEY:{server_pub_b64}".encode())
                    except Exception as e:
                        print(f"[TCP Server] Error enviando pubkey: {e}")

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
        Funcion que permite detener el servidor
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
        self.client_pubkeys.clear()
