import socket
import threading
import time
from core.crypto import generate_keys, export_pubkey, import_pubkey, encrypt_text, decrypt_text


class TCPClient:
    """
    Clase que represta un objeto tipo Cliente TCP, permite iniciar
    una conexión, recibir y enviar mensajes con cifrado RSA.
    """

    def __init__(self, username, host, port, controller):
        """
        Contructor de la clase TCPClient
        :param username: nombre del usuario de la conexion
        :param host: direccion ip del servidor
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
        self.connect_lock = threading.Lock()
        self.dm_queue = []  # Cola de DMs recibidos
        # Generar par de claves del cliente
        self.pubkey, self.privkey = generate_keys()
        self.server_pubkey = None

    def start(self):
        """
        Funcion que permite iniciar el hilo del cliente
        """
        threading.Thread(target=self._connect_loop, daemon=True).start()

    def _connect_loop(self):
        """
        Funcion que crea un bucle de conexion con el servidor.
        Tambien hace el handshake RSA: envia la clave publica del cliente
        y recibe la del servidor.
        """
        while self.running:
            if self.sock is None:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((self.host, self.port))
                    s.settimeout(None)

                    # Registrar usuario y enviar la clave publica del cliente
                    pub_b64 = export_pubkey(self.pubkey)
                    register_msg = f"CONECTADO:{self.username}|{pub_b64}".encode()
                    s.sendall(register_msg)

                    self.sock = s
                    self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                    self.recv_thread.start()
                except Exception as e:
                    self.sock = None
            time.sleep(1)

    def _recv_loop(self):
        """
        Funcion que crea un bucle de recepcion de mensajes.
        Procesa el handshake (PUBKEY) y descifra mensajes recibidos.
        """
        while self.running and self.sock:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break

                decoded = data.decode()

                # Recibir clave publica del servidor
                if decoded.startswith("PUBKEY:"):
                    pubkey_b64 = decoded.split(":", 1)[1]
                    try:
                        self.server_pubkey = import_pubkey(pubkey_b64)
                        print(f"[TCP Client {self.username}] Clave publica del servidor recibida")
                    except Exception as e:
                        print(f"[TCP Client {self.username}] Error importando pubkey del servidor: {e}")
                    continue

                print(f"[TCP Client {self.username}] Mensaje recibido (cifrado)")

                # Descifrar el texto del mensaje para demostrar que llega correctamente
                if decoded.startswith("ALL:") or decoded.startswith("DM:") or decoded.startswith("DM_SENT:"):
                    try:
                        # Saltar el prefijo y el "username:"
                        if decoded.startswith("ALL:"):
                            rest = decoded[4:].split(":", 1)[1].strip()
                        else:
                            rest = decoded.split(":", 2)[2].strip()
                        if "|" in rest:
                            cifrado, _ = rest.rsplit("|", 1)
                        else:
                            cifrado = rest
                        plano = decrypt_text(cifrado, self.privkey)
                        print(f"[TCP Client {self.username}] Texto descifrado: {plano}")
                    except Exception as e:
                        print(f"[TCP Client {self.username}] No se pudo descifrar: {e}")

            except Exception as e:
                print(f"[TCP Client {self.username}] Error recibiendo: {e}")
                break
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.sock = None

    def send(self, message: str, recipient: str = "all"):
        """
        Funcion que permite enviar mensajes al servidor.
        El texto se cifra con la clave publica del servidor antes de enviarse.
        :param message: mensaje que se envia
        :param recipient: destinatario del mensaje ("all" para broadcast)
        :return: True si se envió correctamente, False en caso contrario
        """
        if not self.sock:
            print(f"[TCP Client] Error: Socket no disponible")
            return False

        if not self.server_pubkey:
            print(f"[TCP Client] Error: aun no se recibe la clave publica del servidor")
            return False

        try:
            # Cifrar solo el texto del mensaje
            cifrado = encrypt_text(message, self.server_pubkey)

            if recipient == "all":
                payload = f"ALL:{self.username}: {cifrado}|{time.time()}".encode()
            else:
                payload = f"DM:{recipient}:{self.username}: {cifrado}|{time.time()}".encode()

            self.sock.sendall(payload)
            return True
        except Exception as e:
            print(f"[TCP Client] Error enviando mensaje: {e}")
            self.sock = None
            return False

    def stop(self):
        """
        Funcion que permite cerrar el socket del cliente
        """
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
