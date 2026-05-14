from fastapi import APIRouter, Request
from pydantic import BaseModel
import hashlib
import json
import logging
import os
import re

"""
Modulo que define los endpoints de autenticacion
Persiste usuarios en un archivo JSON
"""
router = APIRouter()
logger = logging.getLogger("audit")

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")

_USERS_FILE = "data/users.json"


def _load_users() -> dict[str, dict]:
    """
    Carga los usuarios desde el archivo JSON
    Si el archivo no existe regresa un diccionario vacio
    """
    if not os.path.exists(_USERS_FILE):
        return {}
    try:
        with open(_USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Auth] Error leyendo usuarios: {e}")
        return {}


def _save_users() -> None:
    """
    Guarda el diccionario de usuarios en el archivo JSON
    """
    os.makedirs("data", exist_ok=True)
    try:
        with open(_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Auth] Error guardando usuarios: {e}")


users: dict[str, dict] = _load_users()


class AuthData(BaseModel):
    email: str
    password: str
    username: str = ""


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/register")
def register(data: AuthData, request: Request):
    email = data.email.strip().lower()
    username = data.username.strip()
    ip = request.client.host if request.client else "unknown"

    if not _EMAIL_RE.match(email):
        logger.warning("REGISTER_FAIL reason=invalid_email ip=%s email=%s", ip, email)
        return {"error": "Formato de correo inválido"}
    if email in users:
        logger.warning("REGISTER_FAIL reason=email_exists ip=%s email=%s", ip, email)
        return {"error": "El correo ya está registrado"}
    if not username or len(username) < 3:
        logger.warning("REGISTER_FAIL reason=short_username ip=%s email=%s", ip, email)
        return {"error": "El nombre de usuario debe tener al menos 3 caracteres"}
    if not _USERNAME_RE.match(username):
        logger.warning("REGISTER_FAIL reason=invalid_username ip=%s email=%s username=%s", ip, email, username)
        return {"error": "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos"}
    if any(u["username"] == username for u in users.values()):
        logger.warning("REGISTER_FAIL reason=username_taken ip=%s email=%s username=%s", ip, email, username)
        return {"error": "El nombre de usuario ya está en uso"}

    users[email] = {
        "email": email,
        "username": username,
        "password": hash_password(data.password),
    }
    _save_users()
    logger.info("REGISTER_OK ip=%s email=%s username=%s", ip, email, username)
    return {"status": "OK", "username": username}


@router.post("/login")
def login(data: AuthData, request: Request):
    email = data.email.strip().lower()
    ip = request.client.host if request.client else "unknown"
    user = users.get(email)
    if not user or user["password"] != hash_password(data.password):
        logger.warning("LOGIN_FAIL ip=%s email=%s", ip, email)
        return {"error": "Correo o contraseña incorrectos"}
    logger.info("LOGIN_OK ip=%s email=%s username=%s", ip, email, user["username"])
    return {"status": "OK", "username": user["username"]}
