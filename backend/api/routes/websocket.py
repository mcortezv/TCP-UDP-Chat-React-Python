from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from api.ws_server import manager

router = APIRouter()


def get_controller(websocket: WebSocket):
    """Dependency para obtener el controller"""
    return websocket.app.state.server


@router.websocket("/ws/{username}")
async def websocket_endpoint(
        websocket: WebSocket,
        username: str,
        controller=Depends(get_controller)
):
    """
    Endpoint WebSocket para conexiones de clientes
    """
    # Asignar controller al manager si no está asignado
    if manager.controller is None:
        manager.set_controller(controller)

    # Verificar que el usuario existe en el sistema
    if username not in controller.clients:
        await websocket.close(code=1008, reason="Usuario no autenticado")
        return

    # Conectar el WebSocket
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
        manager.disconnect(username)
        await manager.send_clients_update()
        print(f"[WS] Usuario {username} desconectado")

    except Exception as e:
        print(f"[WS] Error con {username}: {e}")
        manager.disconnect(username)
        await manager.send_clients_update()