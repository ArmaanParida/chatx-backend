from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
connections = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            for conn in connections:
                if conn != ws:
                    await conn.send_text(data)
    except WebSocketDisconnect:
        connections.remove(ws)