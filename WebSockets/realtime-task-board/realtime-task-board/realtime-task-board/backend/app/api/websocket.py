from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.db.session import SessionLocal
from app.schemas.events import ClientEvent
from app.services.task_service import TaskService
from app.websocket.manager import manager

router = APIRouter()


def serialize_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "column": task.column,
        "created_by": task.created_by,
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    db = SessionLocal()

    try:
        tasks = TaskService.list_tasks(db)
        await manager.send_personal_json(
            websocket,
            {
                "type": "board_state",
                "tasks": [serialize_task(task) for task in tasks],
                "users": manager.online_users(),
            },
        )

        while True:
            payload = await websocket.receive_json()

            try:
                event = ClientEvent(**payload)
            except ValidationError as exc:
                await manager.send_personal_json(
                    websocket,
                    {"type": "error", "message": exc.errors()[0]["msg"]},
                )
                continue

            username = (event.username or manager.active_connections.get(websocket) or "Anonymous").strip()

            if event.type == "join":
                manager.set_username(websocket, username)
                await manager.broadcast_json(
                    {
                        "type": "user_joined",
                        "username": username,
                        "users": manager.online_users(),
                        "message": f"{username} joined the board",
                    }
                )

            elif event.type == "create_task":
                if not event.title or not event.column:
                    await manager.send_personal_json(websocket, {"type": "error", "message": "Title and column are required"})
                    continue
                task = TaskService.create_task(db, event.title, event.column, username)
                await manager.broadcast_json(
                    {
                        "type": "task_created",
                        "task": serialize_task(task),
                        "message": f"{username} created a task",
                    }
                )

            elif event.type == "update_task":
                if not event.task_id or not event.title:
                    await manager.send_personal_json(websocket, {"type": "error", "message": "Task ID and title are required"})
                    continue
                task = TaskService.update_task(db, event.task_id, event.title)
                if task is None:
                    await manager.send_personal_json(websocket, {"type": "error", "message": "Task not found"})
                    continue
                await manager.broadcast_json(
                    {
                        "type": "task_updated",
                        "task": serialize_task(task),
                        "message": f"{username} edited a task",
                    }
                )

            elif event.type == "move_task":
                if not event.task_id or not event.column:
                    await manager.send_personal_json(websocket, {"type": "error", "message": "Task ID and column are required"})
                    continue
                task = TaskService.move_task(db, event.task_id, event.column)
                if task is None:
                    await manager.send_personal_json(websocket, {"type": "error", "message": "Task not found"})
                    continue
                await manager.broadcast_json(
                    {
                        "type": "task_moved",
                        "task": serialize_task(task),
                        "message": f"{username} moved a task to {event.column}",
                    }
                )

            elif event.type == "delete_task":
                if not event.task_id:
                    await manager.send_personal_json(websocket, {"type": "error", "message": "Task ID is required"})
                    continue
                deleted = TaskService.delete_task(db, event.task_id)
                if not deleted:
                    await manager.send_personal_json(websocket, {"type": "error", "message": "Task not found"})
                    continue
                await manager.broadcast_json(
                    {
                        "type": "task_deleted",
                        "task_id": event.task_id,
                        "message": f"{username} deleted a task",
                    }
                )

            elif event.type == "typing":
                await manager.broadcast_json(
                    {
                        "type": "typing",
                        "username": username,
                        "task_id": event.task_id,
                        "message": f"{username} is editing a task",
                    }
                )

    except WebSocketDisconnect:
        username = manager.disconnect(websocket)
        await manager.broadcast_json(
            {
                "type": "user_left",
                "username": username,
                "users": manager.online_users(),
                "message": f"{username} left the board",
            }
        )
    finally:
        db.close()
