from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from core.protocol_selector import ProtocolSelector


def main():
    app = FastAPI()
    server = ProtocolSelector()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    class LoginData(BaseModel):
        username: str

    class MessageData(BaseModel):
        message: str


    @app.post("/run")
    def run(protocol: str):
        return server.run(protocol)

    @app.post("/shutdown")
    def shutdown():
        server.shutdown()
        return {"status": "Servidor detenido"}

    @app.post("/login")
    def login(data: LoginData):
        if data.username in server.clients:
            return {"error": "El usuario ya existe"}
        server.clients.add(data.username)
        return {"status": "OK", "username": data.username}

    @app.post("/send")
    def send(data: MessageData):
        server.history.append(data.message)
        return {"status": "OK"}

    @app.get("/history")
    def get_history():
        return server.history

    @app.delete("/clear")
    def clear():
        server.history.clear()
        return {"status": "Historial Borrado"}

    return app


app = main()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
