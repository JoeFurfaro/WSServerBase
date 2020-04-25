import asyncio
import websockets
import json

def format_packet(x):
    """
    Formats a dictionary or list of dictionaries into a packet string in JSON format to be sent
    """
    if type(x) in (list, dict):
        return json.dumps(x)
    return None

async def root():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        await websocket.send(format_packet({ "type": "request", "code": "auth", "user_name": "joe" }))
        print(await websocket.recv())
        print(await websocket.recv())
        await websocket.send(format_packet({ "type": "request", "code": "foo" }))
        print(await websocket.recv())

        print("done")

asyncio.get_event_loop().run_until_complete(root())
