from fastapi import APIRouter, Request
from pydantic import BaseModel
import hashlib
import logging
import re

"""
Modulo que define los endpoints de autenticacion.
Persiste usuarios en un diccionario en memoria.
"""
router = APIRouter()
logger = logging.getLogger("audit")

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")

users: dict[str, dict] = {}


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
