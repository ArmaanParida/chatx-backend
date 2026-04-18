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
            msg = json.loads(data)

            # send safely
            dead_connections = []

            for conn in connections:
                if conn != ws:
                    try:
                        await conn.send_text(json.dumps(msg))
                    except:
                        dead_connections.append(conn)

            # remove dead ones
            for dc in dead_connections:
                connections.remove(dc)

    except WebSocketDisconnect:
        if ws in connections:
            connections.remove(ws)
