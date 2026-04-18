from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

connections = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            data = await ws.receive_text()

            # parse incoming JSON
            msg = json.loads(data)

            # broadcast to all except sender
            for conn in connections:
                if conn != ws:
                    await conn.send_text(json.dumps(msg))

    except WebSocketDisconnect:
        connections.remove(ws)
