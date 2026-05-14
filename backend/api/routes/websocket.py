from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.ws_server import manager
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger("audit")


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """
    Endpoint WebSocket para conexiones de clientes
    """
    client_ip = websocket.client.host if websocket.client else "unknown"
    controller = websocket.app.state.server

    if manager.controller is None:
        manager.set_controller(controller)

    if username not in controller.clients:
        if controller.is_running():
            print(f"[WS] Usuario {username} no encontrado, recreando cliente...")
            await asyncio.to_thread(controller.create_client, username)
        else:
            logger.warning("WS_REJECT ip=%s username=%s reason=server_not_running", client_ip, username)
            await websocket.accept()
            await websocket.close(code=1008, reason="Usuario no autenticado")
            return

    logger.info("WS_CONNECT ip=%s username=%s", client_ip, username)
    await manager.connect(username, websocket)

    try:
        # Enviar estado inicial con historial
        history = controller.get_chat_history()
        await websocket.send_json({
            "type": "history",
            "messages": history
        })

        # Enviar lista de clientes
        await websocket.send_json({
            "type": "clients_update",
            "clients": list(controller.clients)
        })

        # Notificar a otros usuarios sobre la conexión
        await manager.send_clients_update()

        # Mantener la conexión abierta y escuchar mensajes
        while True:
            data = await websocket.receive_json()

            # Aquí puedes manejar mensajes del cliente si es necesario
            # Por ejemplo, solicitudes de historial, etc.
            if data.get("type") == "get_history":
                history = controller.get_chat_history()
                await websocket.send_json({
                    "type": "history",
                    "messages": history
                })

            elif data.get("type") == "get_dms":
                dms = controller.get_user_dms(username)
                await websocket.send_json({
                    "type": "dms",
                    "messages": dms
                })

    except WebSocketDisconnect:
        # Solo limpiar si esta conexion es la actual para este usuario
        if manager.active_connections.get(username) == websocket:
            logger.info("WS_DISCONNECT ip=%s username=%s", client_ip, username)
            # Remover del dict sin intentar cerrar (ya esta desconectado)
            manager.active_connections.pop(username, None)
            print(f"[WS] Usuario {username} desconectado")
            await manager.send_clients_update()

    except Exception as e:
        print(f"[WS] Error con {username}: {e}")
        if manager.active_connections.get(username) == websocket:
            logger.warning("WS_ERROR ip=%s username=%s error=%s", client_ip, username, str(e))
            manager.active_connections.pop(username, None)
            print(f"[WS] Usuario {username} desconectado (error)")
            await manager.send_clients_update()