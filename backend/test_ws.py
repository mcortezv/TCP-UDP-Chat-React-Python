"""Test directo de WebSocket para diagnosticar el 400"""
import asyncio

async def test_raw():
    """Test con aiohttp para ver la respuesta exacta"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://localhost:8000/ws/TestUser') as ws:
                print("CONECTADO!")
                msg = await ws.receive_json()
                print(f"Primer mensaje: {msg}")
                await ws.close()
    except Exception as e:
        print(f"aiohttp error: {type(e).__name__}: {e}")

async def test_websockets_lib():
    """Test con la librería websockets"""
    import websockets
    try:
        async with websockets.connect('ws://localhost:8000/ws/TestUser') as ws:
            print("CONECTADO con websockets!")
            msg = await ws.recv()
            print(f"Primer mensaje: {msg}")
    except Exception as e:
        print(f"websockets error: {type(e).__name__}: {e}")

async def test_http_upgrade():
    """Test manual del upgrade HTTP -> WS para ver headers de respuesta"""
    import http.client
    conn = http.client.HTTPConnection("localhost", 8000)
    conn.request("GET", "/ws/TestUser", headers={
        "Upgrade": "websocket",
        "Connection": "Upgrade",
        "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
        "Sec-WebSocket-Version": "13",
        "Origin": "http://localhost:5173",
    })
    resp = conn.getresponse()
    print(f"HTTP upgrade response: {resp.status} {resp.reason}")
    print(f"Headers: {dict(resp.getheaders())}")
    body = resp.read()
    if body:
        print(f"Body: {body.decode()}")

async def main():
    print("=== Test 1: HTTP upgrade manual ===")
    await test_http_upgrade()
    print()
    print("=== Test 2: websockets lib ===")
    await test_websockets_lib()
    print()
    try:
        import aiohttp
        print("=== Test 3: aiohttp ===")
        await test_raw()
    except ImportError:
        print("aiohttp no instalado, skip test 3")

asyncio.run(main())
