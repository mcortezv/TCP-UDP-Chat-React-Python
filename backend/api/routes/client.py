from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    username: str

class MessageData(BaseModel):
    message: str
    username: str

@router.post("/login")
def login(req: Request, data: LoginData):
    server = req.app.state.server
    if data.username in server.clients:
        return {"error": "El usuario ya existe"}
    client = server.create_client(data.username)
    return {"status": "OK", "username": data.username}

@router.post("/logout")
def logout(req: Request, data: LoginData):
    server = req.app.state.server
    server.remove_client(data.username)
    return {"status": "OK", "username": data.username}

@router.post("/send")
def send(req: Request, data: MessageData):
    server = req.app.state.server
    if data.username not in server.client_objs:
        return {"error": "Cliente no conectado"}
    client = server.client_objs[data.username]
    client.send(data.message)

    return {"status": "Mensaje enviado"}

@router.get("/history")
def history(req: Request):
    server = req.app.state.server
    return {"history": server.history}

@router.get("/clients")
def list_clients(req: Request):
    server = req.app.state.server
    return {"clients": list(server.clients)}
