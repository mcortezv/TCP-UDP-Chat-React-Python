from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class ProtocolData(BaseModel):
    protocol: str

@router.post("/run")
def run(req: Request, data: ProtocolData):
    server = req.app.state.server
    return server.run(data.protocol)

@router.post("/shutdown")
def shutdown(req: Request):
    server = req.app.state.server
    server.shutdown()
    server.clients.clear()
    return {"status": "Servidor detenido"}

@router.delete("/clear")
def clear(req: Request):
    server = req.app.state.server
    server.history.clear()
    return {"status": "Historial borrado"}

@router.get("/status")
def status(req: Request):
    server = req.app.state.server
    return {
        "running": server.is_running(),
        "protocol": server.protocol,
        "host": server.HOST,
        "port": server.PORT,
        "clients": list(server.clients),
        "history_len": len(server.history)
    }
