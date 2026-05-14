from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.middleware("http")
async def intercept(request: Request, call_next):
    if "Upgrade" in request.headers:
        print("=== UPGRADE REQUEST ===")
        for k, v in request.headers.items():
            print(f"{k}: {v}")
        print("=======================")
    return await call_next(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
