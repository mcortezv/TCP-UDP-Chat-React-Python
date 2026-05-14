import socket
import threading
import time
from core.crypto import generate_keys, export_pubkey, import_pubkey, encrypt_text, decrypt_text


class UDPClient:
    """
    Clase que represta un objeto tipo Cliente UDP, permite recibir y enviar mensajes
    con cifrado RSA.
    """

    def __init__(self, username, host, port, controller):
        """
        Constructor de la clase UDPClient
        :param username: nombre del usuario de la conexion
        :param host: direcccion ip del servidor
        :param port: puerto del servidor
        :param controller: controlador del cliente
        """
        self.username = username
        self.host = host
        self.port = port
        self.controller = controller
        self.sock = None
        self.running = True
        self.recv_thread = None
        self.dm_queue = []  # Cola de DMs recibidos
        # Generar par de claves del cliente
        self.pubkey, self.privkey = generate_keys()
        self.server_pubkey = None

    def start(self):
        """
        Funcion que permite iniciar el hilo del cliente.
        Hace el handshake enviando la clave publica del cliente al servidor.
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("", 0))
            self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self.recv_thread.start()

            # Enviar registro con la clave publica del cliente
            pub_b64 = export_pubkey(self.pubkey)
            register_msg = f"Conectado:{self.username}|{pub_b64}".encode()
            self.sock.sendto(register_msg, (self.host, self.port))
        except Exception as e:
            print(f"[UDP Client] Error iniciando: {e}")

    def _recv_loop(self):
        """
        Funcion que crea un bucle de recepcion de mensajes.
        Procesa el handshake (PUBKEY) y descifra los DMs recibidos.
        """
        if not self.sock:
            return
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                decoded = data.decode()

                # Recibir clave publica del servidor
                if decoded.startswith("PUBKEY:"):
                    pubkey_b64 = decoded.split(":", 1)[1]
                    try:
                        self.server_pubkey = import_pubkey(pubkey_b64)
                        print(f"[UDP Client {self.username}] Clave publica del servidor recibida")
                    except Exception as e:
                        print(f"[UDP Client {self.username}] Error importando pubkey del servidor: {e}")
                    continue

                print(f"[UDP Client {self.username}] Mensaje recibido (cifrado)")

                # Descifrar el texto para demostrar que llega correctamente
                if decoded.startswith("ALL:") or decoded.startswith("DM:") or decoded.startswith("DM_SENT:"):
                    try:
                        if decoded.startswith("ALL:"):
                            rest = decoded[4:].split(":", 1)[1].strip()
                        else:
                            rest = decoded.split(":", 2)[2].strip()
                        if "|" in rest:
                            cifrado, _ = rest.rsplit("|", 1)
                        else:
                            cifrado = rest
                        plano = decrypt_text(cifrado, self.privkey)
                        print(f"[UDP Client {self.username}] Texto descifrado: {plano}")
                    except Exception as e:
                        print(f"[UDP Client {self.username}] No se pudo descifrar: {e}")

                if decoded.startswith("DM:"):
                    msg_content = decoded[3:]
                    self.dm_queue.append(msg_content)

            except Exception as e:
                print(f"[UDP Client {self.username}] Error recibiendo: {e}")
                break

    def get_dms(self):
        """
        Obtiene y limpia la cola de DMs recibidos
        :return: lista de DMs
        """
        dms = self.dm_queue.copy()
        self.dm_queue.clear()
        return dms

    def send(self, message: str, recipient: str = "all"):
        """
        Funcion que permite enviar mensajes al servidor.
        El texto se cifra con la clave publica del servidor antes de enviarse.
        :param message: mensaje que se envia
        :param recipient: destinatario del mensaje ("all" para broadcast)
        :return: True si se envió correctamente, False en caso contrario
        """
        if not self.sock:
            print(f"[UDP Client] Error: Socket no disponible")
            return False

        if not self.server_pubkey:
            print(f"[UDP Client] Error: aun no se recibe la clave publica del servidor")
            return False

        try:
            cifrado = encrypt_text(message, self.server_pubkey)

            if recipient == "all":
                payload = f"ALL:{self.username}: {cifrado}|{time.time()}".encode()
            else:
                payload = f"DM:{recipient}:{self.username}: {cifrado}|{time.time()}".encode()

            self.sock.sendto(payload, (self.host, self.port))
            return True
        except Exception as e:
            print(f"[UDP Client] Error enviando mensaje: {e}")
            return False

    def stop(self):
        """
        Funcion que permite cerrar el socket del cliente
        """
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
