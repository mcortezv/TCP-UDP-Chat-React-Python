from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        # Si ya habia una conexion anterior para este usuario, cerrarla
        old = self.active_connections.get(username)
        if old is not None:
            try:
                await old.close(code=1012, reason="Reemplazado por nueva conexión")
            except Exception:
                pass
        self.active_connections[username] = websocket
        print(f"[WS] Usuario {username} conectado")

    async def disconnect(self, username: str):
        """Remueve y cierra la conexion WebSocket de un usuario"""
        ws = self.active_connections.pop(username, None)
        if ws is not None:
            try:
                await ws.close(code=1000, reason="Desconectado")
            except Exception:
                pass
            print(f"[WS] Usuario {username} desconectado")

    async def disconnect_all(self):
        """Cierra todas las conexiones WebSocket activas"""
        for username in list(self.active_connections.keys()):
            ws = self.active_connections.pop(username, None)
            if ws is not None:
                try:
                    await ws.send_json({"type": "server_shutdown"})
                except Exception:
                    pass
                try:
                    await ws.close(code=1001, reason="Servidor detenido")
                except Exception:
                    pass
                print(f"[WS] Conexión de {username} cerrada (shutdown)")

    async def broadcast_message(self, message: dict, exclude: str = None):
        """Envia un mensaje a todos los usuarios conectados excepto al remitente"""
        disconnected = []
        for username, connection in self.active_connections.items():
            if username != exclude:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(username)

        # Limpiar conexiones muertas
        for username in disconnected:
            await self.disconnect(username)

    async def send_to_user(self, username: str, message: dict):
        """Envia un mensaje a un usuario especifico"""
        if username in self.active_connections:
            try:
                await self.active_connections[username].send_json(message)
                return True
            except:
                await self.disconnect(username)
                return False
        return False

    async def send_clients_update(self):
        """Notifica a todos sobre la lista actualizada de clientes"""
        if not self.controller:
            return

        clients_list = list(self.controller.clients)
        message = {
            "type": "clients_update",
            "clients": clients_list
        }
        await self.broadcast_message(message)


manager = ConnectionManager()


async def notify_new_message(message_data: dict):
    """Notifica a todos los usuarios sobre un nuevo mensaje broadcast"""
    await manager.broadcast_message({
        "type": "new_message",
        "message": message_data
    }, exclude=message_data.get("user"))


async def notify_dm(sender: str, recipient: str, message_data: dict):
    """Notifica sobre un mensaje privado"""
    # Enviar al destinatario
    await manager.send_to_user(recipient, {
        "type": "new_dm",
        "message": message_data
    })

    # Confirmar al remitente (opcional)
    await manager.send_to_user(sender, {
        "type": "dm_sent",
        "message": message_data
    })