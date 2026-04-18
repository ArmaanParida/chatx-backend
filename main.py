from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

users = {}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    username = None

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if "register" in msg:
                username = msg["register"]
                users[username] = ws
                continue

            sender = msg["from"]
            target = msg["to"]

            if target in users:
                try:
                    await users[target].send_text(json.dumps(msg))
                except:
                    pass

    except WebSocketDisconnect:
        if username in users:
            del users[username]
