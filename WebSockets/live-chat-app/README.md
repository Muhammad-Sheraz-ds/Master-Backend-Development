# Live Chat App

A simple beginner-friendly real-time chat application.

## What this project teaches

This project teaches the basic WebSocket idea:

```text
Frontend sends message -> Backend receives it -> Backend broadcasts it -> All frontends update instantly
```

Unlike normal HTTP, WebSocket keeps one connection open between browser and backend.
That means the backend can send new messages to the browser without waiting for page refresh.

## Folder structure

```text
live-chat-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── websocket/
│   │       └── manager.py
│   └── requirements.txt
│
└── frontend/
    ├── index.html
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Backend files

### backend/app/main.py

This is the main FastAPI application.

It creates:

- `/` normal HTTP route for health check
- `/ws` WebSocket route for live chat

The WebSocket route handles these event types:

- `join`
- `chat_message`
- `typing`
- disconnect

### backend/app/websocket/manager.py

This file manages connected users.

It stores:

- active WebSocket connections
- usernames

It also has helper methods for:

- connecting users
- disconnecting users
- broadcasting messages to everyone
- sending message to one user only

### backend/requirements.txt

Python packages needed for backend.

## Frontend files

### frontend/index.html

This is the page structure.

It has:

- join screen
- chat screen
- online users list
- message area
- message input form

### frontend/css/style.css

This controls how the app looks.

It styles:

- join card
- chat layout
- sidebar
- messages
- typing indicator
- mobile layout

### frontend/js/app.js

This is the frontend brain.

It does these jobs:

1. Connects to backend WebSocket
2. Sends join event
3. Sends chat messages
4. Sends typing event
5. Receives backend events
6. Updates HTML on the screen

## Run backend

From project root:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On macOS/Linux, activate environment with:

```bash
source .venv/bin/activate
```

Backend runs at:

```text
http://localhost:8000
```

WebSocket runs at:

```text
ws://localhost:8000/ws
```

## Run frontend

Open this file in your browser:

```text
frontend/index.html
```

Open it in two browser tabs to test live chat.

## Beginner flow

1. Browser opens frontend.
2. User enters name.
3. Frontend opens WebSocket connection to backend.
4. Frontend sends `join` event.
5. Backend saves username.
6. Backend broadcasts joined message.
7. User sends chat message.
8. Backend receives message.
9. Backend broadcasts message to all connected users.
10. Every frontend receives message and displays it.
