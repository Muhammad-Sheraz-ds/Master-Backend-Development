from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.websocket.manager import manager

app = FastAPI(title="Live Chat WebSocket API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Live Chat API is running"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        await manager.send_personal_json(
            websocket,
            {
                "type": "connected",
                "message": "Connected to chat server",
                "users": manager.online_users(),
            },
        )

        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "join":
                username = data.get("username", "Anonymous").strip() or "Anonymous"
                manager.set_username(websocket, username)

                await manager.broadcast_json(
                    {
                        "type": "user_joined",
                        "username": username,
                        "message": f"{username} joined the chat",
                        "users": manager.online_users(),
                        "time": datetime.now().strftime("%H:%M"),
                    }
                )

            elif event_type == "chat_message":
                username = manager.active_connections.get(websocket, "Anonymous")
                message = data.get("message", "").strip()

                if not message:
                    await manager.send_personal_json(
                        websocket,
                        {"type": "error", "message": "Message cannot be empty"},
                    )
                    continue

                await manager.broadcast_json(
                    {
                        "type": "chat_message",
                        "username": username,
                        "message": message,
                        "time": datetime.now().strftime("%H:%M"),
                    }
                )

            elif event_type == "typing":
                username = manager.active_connections.get(websocket, "Anonymous")
                await manager.broadcast_json(
                    {
                        "type": "typing",
                        "username": username,
                        "message": f"{username} is typing...",
                    }
                )

    except WebSocketDisconnect:
        username = manager.disconnect(websocket)
        await manager.broadcast_json(
            {
                "type": "user_left",
                "username": username,
                "message": f"{username} left the chat",
                "users": manager.online_users(),
                "time": datetime.now().strftime("%H:%M"),
            }
        )
