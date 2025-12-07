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
    recipient: str = "all"  # "all" para broadcast, o nombre de usuario específico


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
    :param data: mensaje a enviar (puede incluir destinatario específico)
    """
    server = req.app.state.server

    # Verificar que el cliente existe
    if data.username not in server.client_objs:
        return {"error": "Cliente no conectado. Recarga la pagina e intenta de nuevo."}

    # Verificar si el destinatario existe (si no es broadcast)
    if data.recipient != "all" and data.recipient not in server.clients:
        return {"error": f"El usuario '{data.recipient}' no existe o no está conectado"}

    # Enviar mensaje a traves del cliente
    client = server.client_objs[data.username]

    try:
        # Enviar el mensaje con el destinatario especificado
        success = client.send(data.message, data.recipient)
        if success:
            return {"status": "Mensaje enviado", "recipient": data.recipient}
        else:
            return {"error": "No se pudo enviar el mensaje. El socket no está disponible."}
    except TypeError as e:
        # Error de argumentos - probablemente el método send no acepta recipient
        return {"error": f"Error de compatibilidad: {str(e)}. Verifica que los clientes estén actualizados."}
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
    Funcion que regresa una lista de clientes registrados.
    :param req: servidor singleton
    :return: diccionarrio con los clientes registrados
    """
    server = req.app.state.server
    return {"clients": list(server.clients)}


@router.get("/dms/{username}")
def get_dms(req: Request, username: str):
    """
    Funcion que devuelve los DMs recibidos por un usuario
    :param req: servidor singleton
    :param username: nombre del usuario
    :return: lista de DMs
    """
    server = req.app.state.server

    # Obtener DMs del controlador (que los recibe del servidor TCP/UDP)
    dms = server.get_user_dms(username)

    if dms:
        print(f"[API] Devolviendo {len(dms)} DMs para {username}: {dms}")

    return {"dms": dms}