from fastapi import APIRouter, Request
from pydantic import BaseModel
from api.ws_server import manager
import asyncio

"""
Modulo que define los endpoints para controlar
la configuracion del servidor
"""
router = APIRouter()

class ProtocolData(BaseModel):
    protocol: str

@router.post("/run")
async def run(req: Request, data: ProtocolData):
    """
    Funcion que permite iniciar el servidor
    :param req: sirve para acceder a un servidor singleton
    :param data: tipo de protocolo que se desea ejecutar
    """
    server = req.app.state.server
    result = await asyncio.to_thread(server.run, data.protocol)
    return result

@router.post("/shutdown")
async def shutdown(req: Request):
    """
    Funcion que permite detener el servidor
    Cierra todas las conexiones WebSocket antes de detener
    :param req: sirve para acceder al un servidor singleton
    """
    server = req.app.state.server
    # Cerrar todas las conexiones WebSocket para que los clientes se enteren
    await manager.disconnect_all()
    # Detener el servidor TCP/UDP y los clientes
    await asyncio.to_thread(server.shutdown)
    return {"status": "Servidor detenido"}

@router.delete("/clear")
def clear(req: Request):
    """
    Funcion que permite eliminar el historial de mensajes
    :param req: sirve para acceder al un servidor singleton
    """
    server = req.app.state.server
    server.history.clear()
    return {"status": "Historial borrado"}

@router.get("/status")
def status(req: Request):
    """
    Funcion que permite obtener el status del servidor
    :param req: sirve para acceder al un servidor singleton
    :return: diccionario con el status del servidor
    """
    server = req.app.state.server
    return {
        "running": server.is_running(),
        "protocol": server.protocol,
        "host": server.HOST,
        "port": server.PORT,
        "clients": list(server.clients),
        "history_len": len(server.history)
    }
