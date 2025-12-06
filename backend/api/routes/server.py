from fastapi import APIRouter, Request
from pydantic import BaseModel

"""
Modulo que define los enpoints para controlar 
la configuracion del servidor.
"""
router = APIRouter()

class ProtocolData(BaseModel):
    protocol: str

@router.post("/run")
def run(req: Request, data: ProtocolData):
    """
    Funcion que pemite iniciar el servidor.
    :param req: sirve para acceder a un servidor singleton
    :param data: tipo de protocolo que se desea ejecutar
    """
    server = req.app.state.server
    return server.run(data.protocol)

@router.post("/shutdown")
def shutdown(req: Request):
    """
    Funcion que pemite detener el servidor.
    :param req: sirve para acceder al un servidor singleton
    """
    server = req.app.state.server
    server.shutdown()
    server.clients.clear()
    return {"status": "Servidor detenido"}

@router.delete("/clear")
def clear(req: Request):
    """
    Funcion que pemite eliminar el historial de mensjaes.
    :param req: sirve para acceder al un servidor singleton
    """
    server = req.app.state.server
    server.history.clear()
    return {"status": "Historial borrado"}

@router.get("/status")
def status(req: Request):
    """
    Funcion que pemite obtener el status del servidor.
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
