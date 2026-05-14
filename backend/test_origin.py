import asyncio
import websockets

async def test():
    try:
        async with websockets.connect(
            'ws://localhost:8000/ws/TestUser',
            origin='http://localhost:5173'
        ) as ws:
            print("CONNECTED!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
