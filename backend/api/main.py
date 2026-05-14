import logging
import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware as _CORSMiddleware
from starlette.types import Receive, Scope, Send
from core.server_controller import ServerController
from api.routes.server import router as server_router
from api.routes.client import router as client_router
from api.routes.websocket import router as websocket_router
from api.routes.auth import router as auth_router

os.makedirs("logs", exist_ok=True)
_audit_handler = logging.FileHandler("logs/audit.log")
_audit_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"))
logging.getLogger("audit").addHandler(_audit_handler)
logging.getLogger("audit").setLevel(logging.INFO)

"""
Modulo principal del sistema que permite ejecutar la api
"""


class CORSMiddleware(_CORSMiddleware):
    """
    Subclase de CORSMiddleware que permite conexiones WebSocket
    sin pasar por la validacion CORS
    """
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            await self.app(scope, receive, send)
            return
        await super().__call__(scope, receive, send)


def main():
    """
    Funcion principal que ejecuta la api a la que se conecta
    el front crea la app establece restricciones de acceso
    y establece las rutas del servidor y cliente
    """
    app = FastAPI()
    app.state.server = ServerController()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Rutas de Autenticacion
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])

    # Rutas del Servidor
    app.include_router(server_router, prefix="/server", tags=["Server"])

    # Rutas del Cliente
    app.include_router(client_router, prefix="/client", tags=["Client"])

    # Rutas WebSocket
    app.include_router(websocket_router, tags=["WebSocket"])

    return app


app = main()

if __name__ == "__main__":
    # Uvicorn para desplegar la api en local
    # ws="wsproto" evita que la libreria websockets v15+ rechace conexiones WebSocket
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True, ws="wsproto")