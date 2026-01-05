import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8086/ws"
    async with websockets.connect(uri) as websocket:
        print("Connected to websocket!")
        while True:
            try:
                msg = await websocket.recv()
                print(f"Received: {msg}")
            except Exception as e:
                print("WebSocket error:", e)
                break

if __name__ == "__main__":
    asyncio.run(listen())