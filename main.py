import json

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            for conn in connections:
                if conn != ws:
                    await conn.send_text(json.dumps(msg))

    except WebSocketDisconnect:
        connections.remove(ws)
