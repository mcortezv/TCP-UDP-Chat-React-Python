import socket
import threading
import asyncio
from core.crypto import generate_keys, export_pubkey, import_pubkey, encrypt_text, decrypt_text

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
        self.username_to_addr = {}  # username -> addr
        self.client_pubkeys = {}  # username -> pubkey
        self.init_error = None
        # Generar par de claves del servidor
        self.pubkey, self.privkey = generate_keys()
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
                data, addr = self.server.recvfrom(4096)
                try:
                    decoded = data.decode()

                    # Manejar registro: Conectado:username|<pubkey_b64>
                    if decoded.startswith("Conectado:"):
                        payload = decoded.split(":", 1)[1]
                        if "|" in payload:
                            username, pubkey_b64 = payload.split("|", 1)
                            try:
                                client_pub = import_pubkey(pubkey_b64)
                                self.client_pubkeys[username] = client_pub
                            except Exception as e:
                                print(f"[UDP Server] Error importando pubkey de {username}: {e}")
                        else:
                            username = payload

                        self.clients[addr] = username
                        self.username_to_addr[username] = addr
                        print(f"[UDP Server] Usuario {username} conectado desde {addr}")

                        # Enviar clave publica del servidor al cliente
                        try:
                            server_pub_b64 = export_pubkey(self.pubkey)
                            self.server.sendto(f"PUBKEY:{server_pub_b64}".encode(), addr)
                        except Exception as e:
                            print(f"[UDP Server] Error enviando pubkey: {e}")

                        # Notificar actualización de clientes
                        try:
                            from api.ws_server import manager
                            asyncio.run(manager.send_clients_update())
                        except:
                            pass
                        continue

                    # Registrar cliente si no está registrado (sin pubkey)
                    if addr not in self.clients:
                        self.clients[addr] = f"unknown_{addr[1]}"
                        self.username_to_addr[self.clients[addr]] = addr

                    # Parsear el mensaje
                    if decoded.startswith("ALL:"):
                        # Broadcast - formato: ALL:username: <cifrado>|timestamp
                        msg_content = decoded[4:]
                        parts = msg_content.split(":", 1)

                        if len(parts) >= 2:
                            username = parts[0].strip()
                            rest = parts[1].strip()

                            if "|" in rest:
                                cifrado, timestamp_str = rest.rsplit("|", 1)
                                timestamp = float(timestamp_str)
                            else:
                                cifrado = rest
                                timestamp = 0.0

                            # Descifrar el texto con la clave privada del servidor
                            text = decrypt_text(cifrado, self.privkey)

                            print(f"[UDP Server] Broadcast de {username}: {text}")

                            message_obj = self.controller.add_message_to_history(username, text, timestamp)

                            try:
                                from api.ws_server import notify_new_message
                                asyncio.run(notify_new_message(message_obj))
                            except:
                                pass

                            # Reenviar a cada cliente, cifrado con su clave publica
                            for client_addr, dest_user in list(self.clients.items()):
                                if client_addr == addr:
                                    continue
                                dest_pubkey = self.client_pubkeys.get(dest_user)
                                if not dest_pubkey:
                                    continue
                                try:
                                    cifrado_dest = encrypt_text(text, dest_pubkey)
                                    payload = f"ALL:{username}: {cifrado_dest}|{timestamp}".encode()
                                    self.server.sendto(payload, client_addr)
                                except Exception as e:
                                    self._remove_client(client_addr)

                    elif decoded.startswith("DM:"):
                        # DM - formato: DM:destinatario:remitente: <cifrado>|timestamp
                        parts = decoded.split(":", 3)

                        if len(parts) >= 4:
                            recipient = parts[1]
                            sender = parts[2]
                            rest = parts[3].strip()

                            if "|" in rest:
                                cifrado, timestamp_str = rest.rsplit("|", 1)
                                timestamp = float(timestamp_str)
                            else:
                                cifrado = rest
                                timestamp = 0.0

                            # Descifrar texto
                            text = decrypt_text(cifrado, self.privkey)

                            print(f"[UDP Server] DM de '{sender}' para '{recipient}': {text}")

                            dm_obj = self.controller.add_dm_to_user(recipient, sender, text, timestamp)

                            try:
                                from api.ws_server import notify_dm
                                asyncio.run(notify_dm(sender, recipient, dm_obj))
                            except:
                                pass

                            # Enviar al destinatario UDP cifrado con su pubkey
                            recipient_addr = self.username_to_addr.get(recipient)
                            if recipient_addr:
                                dest_pubkey = self.client_pubkeys.get(recipient)
                                if dest_pubkey:
                                    try:
                                        cifrado_dest = encrypt_text(text, dest_pubkey)
                                        dm_msg = f"DM:{sender}: {cifrado_dest}|{timestamp}".encode()
                                        self.server.sendto(dm_msg, recipient_addr)
                                        print(f"[UDP Server] DM enviado a {recipient}")
                                    except Exception as e:
                                        print(f"[UDP Server] Error enviando DM: {e}")
                                        self._remove_client(recipient_addr)

                            # Confirmacion al remitente cifrada con su pubkey
                            sender_pubkey = self.client_pubkeys.get(sender)
                            if sender_pubkey:
                                try:
                                    cifrado_sender = encrypt_text(text, sender_pubkey)
                                    confirm_msg = f"DM_SENT:{sender}: {cifrado_sender}|{timestamp}".encode()
                                    self.server.sendto(confirm_msg, addr)
                                    print(f"[UDP Server] Confirmacion enviada al remitente")
                                except Exception as e:
                                    print(f"[UDP Server] Error enviando confirmacion: {e}")

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
                if username in self.client_pubkeys:
                    del self.client_pubkeys[username]

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
        self.client_pubkeys.clear()
        if self.server:
            try:
                self.server.close()
            except Exception as e:
                pass
