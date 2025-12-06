import socket
import threading


class UDPServer(threading.Thread):
    def __init__(self, ip, port, controller):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.controller = controller
        self.server = None
        self.running = False
        self.clients = {}  # addr -> username
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
                        continue

                    # Agregar al historial
                    self.controller.history.append(decoded)
                except Exception as e:
                    print(f"[UDP Server] Error decodificando: {e}")
                    continue

                # Registrar cliente si no esta registrado
                if addr not in self.clients:
                    self.clients[addr] = f"unknown_{addr[1]}"

                # Broadcast a todos menos al remitente
                sent_count = 0
                for client_addr in list(self.clients.keys()):
                    if client_addr != addr:
                        try:
                            self.server.sendto(data, client_addr)
                            sent_count += 1
                        except Exception as e:
                            try:
                                del self.clients[client_addr]
                            except:
                                pass
            except socket.timeout:
                # Timeout normal, continuar el bucle
                continue
            except Exception as e:
                break

    def stop(self):
        self.running = False
        self.clients.clear()
        if self.server:
            try:
                self.server.close()
            except Exception as e:
                pass
