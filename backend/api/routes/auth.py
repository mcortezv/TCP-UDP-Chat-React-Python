from fastapi import APIRouter, Request
from pydantic import BaseModel
import hashlib

"""
Modulo que define los endpoints de autenticacion.
Persiste usuarios en un diccionario en memoria.
"""
router = APIRouter()

users: dict[str, dict] = {}


class AuthData(BaseModel):
    email: str
    password: str
    username: str = ""


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/register")
def register(data: AuthData):
    if data.email in users:
        return {"error": "El correo ya está registrado"}
    if not data.username or len(data.username.strip()) < 3:
        return {"error": "El nombre de usuario debe tener al menos 3 caracteres"}
    username = data.username.strip()
    if any(u["username"] == username for u in users.values()):
        return {"error": "El nombre de usuario ya está en uso"}
    users[data.email] = {
        "email": data.email,
        "username": username,
        "password": hash_password(data.password),
    }
    return {"status": "OK", "username": username}


@router.post("/login")
def login(data: AuthData):
    user = users.get(data.email)
    if not user:
        return {"error": "Correo o contraseña incorrectos"}
    if user["password"] != hash_password(data.password):
        return {"error": "Correo o contraseña incorrectos"}
    return {"status": "OK", "username": user["username"]}
