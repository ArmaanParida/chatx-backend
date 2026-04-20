import json
import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# 🧠 In-memory online users
users = {}

# 💾 Database
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    message TEXT,
    delivered INTEGER DEFAULT 0
)
""")

conn.commit()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    current_user = None

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            # 🔐 REGISTER
            if "register_user" in msg:
                username = msg["username"]
                password = msg["password"]

                cursor.execute(
                    "INSERT OR IGNORE INTO users VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()

                await ws.send_text(json.dumps({"status": "registered"}))
                continue

            # 🔐 LOGIN
            if "login" in msg:
                username = msg["username"]
                password = msg["password"]

                cursor.execute(
                    "SELECT * FROM users WHERE username=? AND password=?",
                    (username, password)
                )
                user = cursor.fetchone()

                if user:
                    current_user = username
                    users[username] = ws

                    await ws.send_text(json.dumps({"status": "login_success"}))

                    # 📥 SEND OLD MESSAGES
                    cursor.execute(
                        "SELECT sender, message FROM messages WHERE receiver=? AND delivered=0",
                        (username,)
                    )
                    rows = cursor.fetchall()

                    for sender, message in rows:
                        await ws.send_text(json.dumps({
                            "from": sender,
                            "msg": message
                        }))

                    cursor.execute(
                        "UPDATE messages SET delivered=1 WHERE receiver=?",
                        (username,)
                    )
                    conn.commit()

                    # 👥 SEND USER LIST
                    await broadcast_users()

                else:
                    await ws.send_text(json.dumps({"status": "login_failed"}))

                continue

            # 💬 MESSAGE
            sender = msg["from"]
            target = msg["to"]
            text = msg["msg"]

            # 💾 STORE
            cursor.execute(
                "INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                (sender, target, text)
            )
            conn.commit()

            # 📡 SEND if online
            if target in users:
                await users[target].send_text(json.dumps({
                    "from": sender,
                    "msg": text
                }))

    except WebSocketDisconnect:
        if current_user and current_user in users:
            del users[current_user]
            await broadcast_users()


async def broadcast_users():
    user_list = list(users.keys())

    for u in users:
        try:
            await users[u].send_text(json.dumps({
                "type": "users",
                "users": user_list
            }))
        except:
            pass
