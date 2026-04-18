from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

users = {}  # username → websocket

async def broadcast_user_list():
    user_list = list(users.keys())
    msg = json.dumps({"type": "users", "users": user_list})

    dead = []
    for u, ws in users.items():
        try:
            await ws.send_text(msg)
        except:
            dead.append(u)

    for d in dead:
        del users[d]

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

                await broadcast_user_list()
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
            await broadcast_user_list()
