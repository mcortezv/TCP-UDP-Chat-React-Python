from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        print(f"[WS] Usuario {username} conectado")

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
            print(f"[WS] Usuario {username} desconectado")

    async def broadcast_message(self, message: dict, exclude: str = None):
        """Envía un mensaje a todos los usuarios conectados excepto al remitente"""
        disconnected = []
        for username, connection in self.active_connections.items():
            if username != exclude:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(username)

        # Limpiar conexiones muertas
        for username in disconnected:
            self.disconnect(username)

    async def send_to_user(self, username: str, message: dict):
        """Envía un mensaje a un usuario específico"""
        if username in self.active_connections:
            try:
                await self.active_connections[username].send_json(message)
                return True
            except:
                self.disconnect(username)
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
    """Notifica sobre un mensaje directo"""
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