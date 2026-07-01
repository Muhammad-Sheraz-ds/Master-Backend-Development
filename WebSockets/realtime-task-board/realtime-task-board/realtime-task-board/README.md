# Real-Time Collaborative Task Board

A beginner-friendly project for learning **WebSockets with Python**.

This app is like a small Trello board. Multiple users can open the same board in different browser tabs. When one user creates, edits, deletes, or moves a task, all other users see the change instantly without refreshing the page.

---

## What you will learn

By reading and running this project, you will learn:

- What a WebSocket is
- How frontend JavaScript talks to a Python backend in real time
- How FastAPI handles WebSocket connections
- How to broadcast one user's action to all connected users
- How to save tasks in SQLite
- How to organize backend code in a clean folder structure
- How to organize frontend JavaScript into small files
- How drag-and-drop works in the browser

---

## Normal HTTP vs WebSocket

Before WebSockets, most beginner apps use normal HTTP.

With normal HTTP:

```text
Browser sends request -> Backend sends response -> Connection closes
```

Example:

```text
User clicks button
Browser sends POST /tasks
Backend saves task
Backend returns response
Connection ends
```

That works, but it is not ideal for real-time apps.

With WebSockets:

```text
Browser connects once -> Connection stays open -> Both sides can send messages anytime
```

That means:

- Frontend can send a message to backend anytime
- Backend can send a message to frontend anytime
- Backend can send updates to all users instantly
- No page refresh is needed

In this project, WebSockets are used for the live task board.

---

## Project features

- User enters a name before joining
- Online users list
- Create tasks
- Edit task titles
- Delete tasks
- Move tasks between columns
- Drag-and-drop task movement
- Live updates for all connected users
- Activity log
- Typing/editing indicator
- SQLite database persistence
- New users receive the existing board state when they join

---

## Folder structure

```text
realtime-task-board/
├── README.md
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── websocket.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py
│       ├── db/
│       │   ├── __init__.py
│       │   └── session.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── task.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── events.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── task_service.py
│       └── websocket/
│           ├── __init__.py
│           └── manager.py
└── frontend/
    ├── index.html
    ├── css/
    │   └── styles.css
    └── js/
        ├── api.js
        ├── ui.js
        └── app.js
```

---

# How to run the project

## 1. Start the backend

Open a terminal in the project folder.

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

The backend will run at:

```text
http://localhost:8000
```

The WebSocket URL is:

```text
ws://localhost:8000/ws
```

You can test the backend health check here:

```text
http://localhost:8000/health
```

---

## 2. Start the frontend

Open this file in your browser:

```text
frontend/index.html
```

To test real-time behavior:

1. Open `frontend/index.html` in one browser tab.
2. Open the same file in another browser tab.
3. Join with different names.
4. Create, edit, delete, and move tasks.
5. Watch both tabs update instantly.

---

# Backend explanation

The backend is built with:

- FastAPI
- WebSockets
- SQLAlchemy
- SQLite
- Pydantic

The backend is inside this folder:

```text
backend/app/
```

---

## `backend/requirements.txt`

This file lists the Python packages needed by the backend.

Typical dependencies are:

```text
fastapi
uvicorn
sqlalchemy
pydantic
```

Purpose:

- `fastapi` creates the backend app
- `uvicorn` runs the backend server
- `sqlalchemy` talks to the SQLite database
- `pydantic` validates incoming WebSocket messages

---

## `backend/app/main.py`

This is the main entry point of the backend.

Important code:

```python
app = FastAPI(title=settings.app_name)
```

This creates the FastAPI app.

```python
Base.metadata.create_all(bind=engine)
```

This creates database tables automatically when the app starts.

```python
app.include_router(websocket_router)
```

This connects the WebSocket route to the main app.

```python
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

This is a simple test route. If you open `/health`, it should return:

```json
{ "status": "ok" }
```

Purpose of this file:

- Create FastAPI app
- Enable CORS
- Create database tables
- Register WebSocket routes
- Provide a health check route

---

## `backend/app/core/config.py`

This file stores app settings in one place.

```python
class Settings(BaseModel):
    app_name: str = "Real-Time Task Board"
    database_url: str = "sqlite:///./task_board.db"
    cors_origins: list[str] = ["*"]
```

Purpose:

- `app_name` is the backend app name
- `database_url` tells SQLAlchemy where the SQLite database is
- `cors_origins` controls which frontend origins can talk to backend

Beginner note:

Keeping settings in one file is better than spreading them across the project. Later, if you change from SQLite to PostgreSQL, you mostly change the database URL here.

---

## `backend/app/db/session.py`

This file sets up the database connection.

```python
engine = create_engine(settings.database_url)
```

The engine is the main database connection object.

```python
SessionLocal = sessionmaker(...)
```

A session is used to talk to the database.

```python
class Base(DeclarativeBase):
    pass
```

All database models inherit from `Base`.

Purpose:

- Connect to SQLite
- Create database sessions
- Provide a base class for database models

Beginner note:

Think of a database session as a temporary conversation with the database. You open it, do work, commit changes, then close it.

---

## `backend/app/models/task.py`

This file defines the database table for tasks.

```python
class Task(Base):
    __tablename__ = "tasks"
```

This means SQLAlchemy will create a table named `tasks`.

Fields:

```python
id
```

Unique task ID.

```python
title
```

Task title shown on the board.

```python
column
```

Task column. It can be:

```text
todo
in_progress
done
```

```python
created_by
```

Username of the person who created the task.

```python
created_at
updated_at
```

Timestamps for creation and update.

Purpose:

- Define the shape of the `tasks` database table
- Tell SQLAlchemy what task data should be saved

---

## `backend/app/schemas/events.py`

This file defines the shape of WebSocket messages.

The frontend sends JSON messages like this:

```json
{
  "type": "create_task",
  "username": "Ali",
  "title": "Learn WebSockets",
  "column": "todo"
}
```

The backend uses Pydantic to validate that message.

Important code:

```python
BoardColumn = Literal["todo", "in_progress", "done"]
```

This means only these three column names are allowed.

```python
EventType = Literal[
    "join",
    "create_task",
    "update_task",
    "move_task",
    "delete_task",
    "typing",
]
```

This defines allowed event types.

```python
class ClientEvent(BaseModel):
    type: EventType
    username: str | None = None
    task_id: int | None = None
    title: str | None = None
    column: BoardColumn | None = None
```

This is the expected structure of messages coming from the frontend.

Purpose:

- Validate incoming WebSocket messages
- Prevent invalid columns
- Prevent unexpected event names
- Make backend code safer and clearer

Beginner note:

Schemas are not database tables. Schemas are for validating data that enters or leaves your app.

---

## `backend/app/services/task_service.py`

This file contains the task business logic.

It has functions like:

```python
list_tasks()
create_task()
update_task()
move_task()
delete_task()
```

Example:

```python
@staticmethod
def create_task(db, title, column, created_by):
    task = Task(title=title.strip(), column=column, created_by=created_by)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

What happens here:

1. Create a new `Task` object
2. Add it to the database session
3. Commit it to save permanently
4. Refresh it so it gets its new database ID
5. Return the saved task

Purpose:

- Keep database logic away from WebSocket route logic
- Make code easier to read
- Make task logic reusable

Beginner note:

The WebSocket route should not contain all database logic. That makes the file too large. A service file keeps the project cleaner.

---

## `backend/app/websocket/manager.py`

This file manages connected WebSocket users.

Important code:

```python
self.active_connections: dict[WebSocket, str] = {}
```

This stores connected users.

The key is the WebSocket connection.
The value is the username.

Example idea:

```text
connection_1 -> Ali
connection_2 -> Sara
connection_3 -> Ahmed
```

### `connect()`

```python
async def connect(self, websocket):
    await websocket.accept()
    self.active_connections[websocket] = "Anonymous"
```

This accepts a new WebSocket connection.

### `set_username()`

```python
def set_username(self, websocket, username):
    self.active_connections[websocket] = username
```

This changes the user from `Anonymous` to their real name.

### `disconnect()`

```python
def disconnect(self, websocket):
    return self.active_connections.pop(websocket, "Anonymous")
```

This removes the user when they leave.

### `online_users()`

```python
def online_users(self):
    return sorted(set(self.active_connections.values()))
```

This returns all online usernames.

### `send_personal_json()`

Sends a message to one user only.

Used when:

- New user needs board state
- One user sends invalid data
- One user needs an error message

### `broadcast_json()`

Sends a message to every connected user.

Used when:

- A task is created
- A task is edited
- A task is moved
- A task is deleted
- A user joins
- A user leaves

Purpose:

- Track active WebSocket connections
- Send private messages
- Broadcast messages to everyone

---

## `backend/app/api/websocket.py`

This is the most important backend file for WebSockets.

It defines this route:

```python
@router.websocket("/ws")
```

That means the frontend connects to:

```text
ws://localhost:8000/ws
```

Main flow:

```python
await manager.connect(websocket)
```

Accept the WebSocket connection.

```python
tasks = TaskService.list_tasks(db)
```

Load saved tasks from the database.

```python
await manager.send_personal_json(websocket, {...})
```

Send the current board state to the newly connected user only.

Then the backend enters a loop:

```python
while True:
    payload = await websocket.receive_json()
```

This waits for messages from the frontend.

Example message:

```json
{
  "type": "move_task",
  "username": "Ali",
  "task_id": 1,
  "column": "done"
}
```

Then the backend checks the event type:

```python
if event.type == "join":
```

User joined.

```python
elif event.type == "create_task":
```

Create a task in the database, then broadcast it.

```python
elif event.type == "update_task":
```

Update task title, then broadcast it.

```python
elif event.type == "move_task":
```

Move task to another column, then broadcast it.

```python
elif event.type == "delete_task":
```

Delete task, then broadcast it.

```python
elif event.type == "typing":
```

Tell other users someone is editing.

Purpose:

- Receive WebSocket messages
- Validate messages
- Call task service functions
- Broadcast results to all users
- Handle user disconnects

---

# Frontend explanation

The frontend is built with:

- HTML
- CSS
- Vanilla JavaScript

No React, Vue, or build tool is required.

The frontend is inside:

```text
frontend/
```

---

## `frontend/index.html`

This is the main page.

Important sections:

### Login screen

```html
<section id="login" class="login-card">
```

This is where the user enters their name.

### Main board app

```html
<section id="boardApp" class="hidden">
```

This contains the board, but it is hidden until the user joins.

### Online users

```html
<ul id="usersList"></ul>
```

JavaScript fills this list with connected users.

### Create task form

```html
<form id="taskForm" class="task-form">
```

This lets the user create a new task.

### Board columns

```html
<div class="column" data-column="todo">
<div class="column" data-column="in_progress">
<div class="column" data-column="done">
```

Each column has a `data-column` value. JavaScript uses this value when a task is dropped into a column.

### Activity log

```html
<ul id="activityLog"></ul>
```

Shows messages like:

```text
Ali created a task
Sara moved a task to done
Ahmed deleted a task
```

### JavaScript files

```html
<script src="js/api.js"></script>
<script src="js/ui.js"></script>
<script src="js/app.js"></script>
```

The order matters:

1. `api.js` defines the WebSocket class
2. `ui.js` defines UI helper functions
3. `app.js` connects everything together

---

## `frontend/css/styles.css`

This file styles the app.

It controls:

- Page layout
- Login card
- Board columns
- Task cards
- Buttons
- Drag-over effect
- Activity panel
- Mobile responsiveness

Important class:

```css
.hidden {
  display: none;
}
```

This hides the board before the user joins.

Important drag style:

```css
.column.drag-over {
  outline: 3px dashed #2563eb;
}
```

This shows a border when a task is dragged over a column.

---

## `frontend/js/api.js`

This file creates a small WebSocket wrapper class.

```javascript
class BoardSocket {
```

This class hides the low-level WebSocket details.

### `connect()`

```javascript
this.socket = new WebSocket(this.url);
```

This opens the WebSocket connection.

```javascript
this.socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  this.emit(data.type, data);
};
```

When the backend sends a message, frontend parses the JSON and calls the correct event handler.

### `on()`

```javascript
on(eventName, callback)
```

Registers a function for a specific event.

Example:

```javascript
boardSocket.on("task_created", (event) => {
  // update UI
});
```

### `send()`

```javascript
send(payload) {
  this.socket.send(JSON.stringify(payload));
}
```

Sends JSON data to the backend.

Purpose:

- Open WebSocket connection
- Send JSON messages
- Receive JSON messages
- Route events to the right frontend function

---

## `frontend/js/ui.js`

This file handles screen updates.

It does not talk directly to the backend.
It only updates the page.

### Global state

```javascript
const state = {
  username: "",
  tasks: new Map(),
};
```

This stores current frontend data.

`tasks` is a `Map` because each task has an ID.

Example:

```text
1 -> { id: 1, title: "Learn WebSockets", column: "todo" }
2 -> { id: 2, title: "Build frontend", column: "done" }
```

### `showBoard()`

Hides login screen and shows the board.

### `renderUsers()`

Updates the online users list.

### `renderBoard()`

Clears all columns and redraws tasks.

### `createTaskCard()`

Creates the HTML for one task card.

It also adds:

- Edit button
- Delete button
- Drag behavior

### `addActivity()`

Adds a message to the activity log.

### `showTyping()`

Shows a temporary message like:

```text
Ali is editing a task
```

Purpose:

- Keep DOM manipulation in one file
- Make frontend easier to understand
- Separate UI code from WebSocket code

---

## `frontend/js/app.js`

This is the main frontend logic file.

It connects:

- UI
- WebSocket API
- User actions
- Backend events

Important line:

```javascript
const socketUrl = "ws://localhost:8000/ws";
```

This is the backend WebSocket URL.

```javascript
const boardSocket = new BoardSocket(socketUrl);
```

This creates the WebSocket client.

### Listening to backend events

Example:

```javascript
boardSocket.on("task_created", (event) => {
  state.tasks.set(event.task.id, event.task);
  renderBoard();
  addActivity(event.message);
});
```

When backend says a task was created:

1. Save task in frontend state
2. Redraw board
3. Add activity message

### Sending frontend events

Example:

```javascript
boardSocket.send({
  type: "create_task",
  username: state.username,
  title,
  column: taskColumnInput.value,
});
```

This sends a task creation request to backend.

### Drag-and-drop

When a user drags a task, the task ID is stored:

```javascript
event.dataTransfer.setData("text/plain", String(task.id));
```

When a user drops it into a column:

```javascript
const taskId = Number(event.dataTransfer.getData("text/plain"));
const targetColumn = column.dataset.column;
```

Then frontend sends this to backend:

```javascript
boardSocket.send({
  type: "move_task",
  username: state.username,
  task_id: taskId,
  column: targetColumn,
});
```

Purpose:

- Start WebSocket connection
- Handle user clicks and form submissions
- Send messages to backend
- Listen for backend broadcasts
- Update UI through helper functions

---

# WebSocket event flow

## When a user joins

```text
Frontend opens WebSocket connection
Backend accepts connection
Backend sends existing board_state to that user
User enters name and clicks Join
Frontend sends join event
Backend stores username
Backend broadcasts user_joined to everyone
Frontend updates online users list
```

Frontend sends:

```json
{
  "type": "join",
  "username": "Ali"
}
```

Backend broadcasts:

```json
{
  "type": "user_joined",
  "username": "Ali",
  "users": ["Ali", "Sara"],
  "message": "Ali joined the board"
}
```

---

## When a user creates a task

```text
User fills task form
Frontend sends create_task
Backend validates message
Backend saves task in SQLite
Backend broadcasts task_created
All frontends add task to state
All frontends redraw board
```

Frontend sends:

```json
{
  "type": "create_task",
  "username": "Ali",
  "title": "Learn WebSockets",
  "column": "todo"
}
```

Backend broadcasts:

```json
{
  "type": "task_created",
  "task": {
    "id": 1,
    "title": "Learn WebSockets",
    "column": "todo",
    "created_by": "Ali"
  },
  "message": "Ali created a task"
}
```

---

## When a user moves a task

```text
User drags task card to another column
Frontend sends move_task
Backend updates task column in SQLite
Backend broadcasts task_moved
All frontends redraw board
```

Frontend sends:

```json
{
  "type": "move_task",
  "username": "Ali",
  "task_id": 1,
  "column": "done"
}
```

Backend broadcasts:

```json
{
  "type": "task_moved",
  "task": {
    "id": 1,
    "title": "Learn WebSockets",
    "column": "done",
    "created_by": "Ali"
  },
  "message": "Ali moved a task to done"
}
```

---

## When a user edits a task

```text
User clicks Edit
Frontend sends typing event
Other users see editing indicator
User enters new title
Frontend sends update_task
Backend updates database
Backend broadcasts task_updated
All frontends redraw board
```

---

## When a user deletes a task

```text
User clicks Delete
Frontend sends delete_task
Backend deletes task from SQLite
Backend broadcasts task_deleted
All frontends remove task from board
```

---

# Why this structure is good

This project avoids putting all code in one file.

Instead, each file has one job:

```text
main.py              Starts the app
config.py            Stores settings
session.py           Connects to database
task.py              Defines database table
events.py            Validates messages
task_service.py      Handles task database logic
manager.py           Tracks WebSocket users
websocket.py         Handles WebSocket route and events
api.js               Handles WebSocket client
ui.js                Handles page rendering
app.js               Connects UI and WebSocket logic
styles.css           Handles design
index.html           Defines page structure
```

This is easier to understand, debug, and grow.

---

# Important beginner concepts

## 1. WebSocket connection

A WebSocket connection is a long-running connection between browser and backend.

In frontend:

```javascript
new WebSocket("ws://localhost:8000/ws")
```

In backend:

```python
@router.websocket("/ws")
```

These two must match.

---

## 2. Event type

Every WebSocket message has a `type`.

Example:

```json
{ "type": "create_task" }
```

The backend uses `type` to decide what to do.

The frontend also uses `type` to decide how to update the page.

---

## 3. Broadcast

Broadcast means sending one message to all connected users.

Example:

```text
Ali creates task
Backend broadcasts to Ali, Sara, Ahmed
Everyone sees the new task
```

---

## 4. Persistence

Persistence means data is saved even after refresh.

This project uses SQLite.

When you create a task, it is saved in:

```text
task_board.db
```

This file is created automatically inside the backend folder when the app runs.

---

## 5. Frontend state

The frontend keeps a temporary copy of tasks in memory:

```javascript
state.tasks
```

When backend sends updates, frontend updates this state and redraws the page.

---

# How to read the code as a beginner

Read in this order:

1. `frontend/index.html`
2. `frontend/js/app.js`
3. `frontend/js/api.js`
4. `backend/app/api/websocket.py`
5. `backend/app/websocket/manager.py`
6. `backend/app/services/task_service.py`
7. `backend/app/models/task.py`
8. `backend/app/db/session.py`
9. `backend/app/main.py`

This order helps because you first understand what the user sees, then how messages travel, then how data is stored.

---

# Practice tasks for learning

Try these one by one.

## Easy

- Change the app title
- Add a new column called `Blocked`
- Change activity messages
- Add a confirmation before deleting a task

## Medium

- Add task description
- Add task priority
- Add task due date
- Show task creation time
- Show who last edited the task

## More advanced

- Replace `window.prompt()` with a custom edit form
- Add authentication
- Add multiple boards
- Use PostgreSQL instead of SQLite
- Add tests for task service
- Deploy backend and frontend online

---

# Common errors

## Backend not running

If frontend says disconnected, make sure backend is running:

```bash
uvicorn app.main:app --reload
```

## Wrong folder

Run backend commands from the `backend` folder, not the root folder.

Correct:

```bash
cd backend
uvicorn app.main:app --reload
```

## Port already in use

If port `8000` is already busy, run:

```bash
uvicorn app.main:app --reload --port 8001
```

Then update this line in `frontend/js/app.js`:

```javascript
const socketUrl = "ws://localhost:8001/ws";
```

## PowerShell activation error

If Windows blocks activation, run PowerShell as administrator and execute:

```powershell
Set-ExecutionPolicy RemoteSigned
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

---

# Final mental model

Think of the app like this:

```text
Browser tab 1 ┐
Browser tab 2 ├── WebSocket ── FastAPI backend ── SQLite database
Browser tab 3 ┘
```

When one browser sends an event, the backend handles it, saves changes if needed, then broadcasts the result to every connected browser.

That is the core idea of WebSockets.
