from fastapi import APIRouter, Request
from pydantic import BaseModel

"""
Modulo que define los enpoints para controlar al cliente.
"""
router = APIRouter()

class LoginData(BaseModel):
    username: str

class MessageData(BaseModel):
    message: str
    username: str

@router.post("/login")
def login(req: Request, data: LoginData):
    """
    Funcion que pemite iniciar un nuevo cliente.
    :param req: acceso a servidor singleton
    :param data: nombre del usuario que quiere crear un nuevo cliente
    :return: nombre del usuario
    """
    server = req.app.state.server

    # Verificar que hay un servidor corriendo
    if not server.is_running():
        return {"error": "No hay servidor corriendo. Inicia el servidor primero."}

    # Verificar si el usuario ya existe
    if data.username in server.clients:
        print(f"[API] ERROR: Usuario {data.username} ya existe")
        return {"error": "El usuario ya existe"}

    # Crear cliente
    client = server.create_client(data.username)
    if client is None:
        return {"error": "No se pudo crear el cliente"}
    return {"status": "OK", "username": data.username}

@router.post("/logout")
def logout(req: Request, data: LoginData):
    """
    Funcion que permite remover al cliente del servidor.
    :param req: acceso a servidor singleton
    :param data: nombre del usuario que quiere remover
    :return: nombre del usuario
    """
    server = req.app.state.server
    server.remove_client(data.username)
    return {"status": "OK", "username": data.username}

@router.post("/send")
def send(req: Request, data: MessageData):
    """
    Funcion que permite enviar un mensaje al servidor.
    :param req: servidor singleton
    :param data: mensaje a enviar
    """
    server = req.app.state.server

    # Verificar que el cliente existe
    if data.username not in server.client_objs:
        return {"error": "Cliente no conectado. Recarga la pagina e intenta de nuevo."}

    # Enviar mensaje a traves del cliente
    client = server.client_objs[data.username]

    try:
        success = client.send(data.message)
        if success:
            return {"status": "Mensaje enviado"}
        else:
            pass
    except Exception as e:
        return {"error": f"Error al enviar: {str(e)}"}

@router.get("/history")
def history(req: Request):
    """
    Funcion que devuelve el historial de mensajes que han pasado por el servidor.
    :param req: servidor singleton
    :return: diccionarrio con el historial de mensajes
    """
    server = req.app.state.server
    return {"history": server.history}

@router.get("/clients")
def list_clients(req: Request):
    """
    Funcion que regresa una lista de clientes registrados (Solo TCP). No lo usamos al final xd
    :param req: servidor singleton
    :return: diccionarrio con los clientes registrados
    """
    server = req.app.state.server
    return {"clients": list(server.clients)}