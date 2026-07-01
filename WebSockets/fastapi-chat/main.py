from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Single Chat</title>
</head>
<body>
    <h2>FastAPI 1-to-1 Chat</h2>

    <input id="username" placeholder="Your name">
    <button onclick="connect()">Connect</button>

    <br><br>

    <input id="message" placeholder="Type message">
    <button onclick="sendMessage()">Send</button>

    <ul id="messages"></ul>

    <script>
        let ws;

        function connect() {
            const username = document.getElementById("username").value;
            ws = new WebSocket(`ws://localhost:8000/ws/${username}`);

            ws.onmessage = function(event) {
                const li = document.createElement("li");
                li.textContent = event.data;
                document.getElementById("messages").appendChild(li);
            };
        }

        function sendMessage() {
            const message = document.getElementById("message").value;
            ws.send(message);
            document.getElementById("message").value = "";
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def send_to_other_user(self, sender: str, message: str):
        for username, websocket in self.active_connections.items():
            if username != sender:
                await websocket.send_text(f"{sender}: {message}")


manager = ConnectionManager()


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(username, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.send_to_other_user(username, message)

    except WebSocketDisconnect:
        manager.disconnect(username)