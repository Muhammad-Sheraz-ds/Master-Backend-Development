from fastapi import WebSocket


class ConnectionManager:
    """Stores active WebSocket connections and sends messages to users."""

    def __init__(self):
        self.active_connections: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = "Anonymous"

    def set_username(self, websocket: WebSocket, username: str):
        self.active_connections[websocket] = username

    def disconnect(self, websocket: WebSocket) -> str:
        username = self.active_connections.get(websocket, "Anonymous")
        self.active_connections.pop(websocket, None)
        return username

    def online_users(self) -> list[str]:
        return list(self.active_connections.values())

    async def send_personal_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

    async def broadcast_json(self, data: dict):
        disconnected = []

        for websocket in self.active_connections:
            try:
                await websocket.send_json(data)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)


manager = ConnectionManager()
