from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[websocket] = "Anonymous"

    def set_username(self, websocket: WebSocket, username: str) -> None:
        self.active_connections[websocket] = username

    def disconnect(self, websocket: WebSocket) -> str:
        return self.active_connections.pop(websocket, "Anonymous")

    def online_users(self) -> list[str]:
        return sorted(set(self.active_connections.values()))

    async def send_personal_json(self, websocket: WebSocket, data: dict) -> None:
        await websocket.send_json(data)

    async def broadcast_json(self, data: dict) -> None:
        disconnected: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except RuntimeError:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()
