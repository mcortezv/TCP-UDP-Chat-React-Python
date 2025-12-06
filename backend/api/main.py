from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.server_controller import ServerController
from routes.server import router as server_router
from routes.client import router as client_router


def main():
    app = FastAPI()
    app.state.server = ServerController()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(server_router, prefix="/server", tags=["Server"])
    app.include_router(client_router, prefix="/client", tags=["Client"])

    return app


app = main()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
