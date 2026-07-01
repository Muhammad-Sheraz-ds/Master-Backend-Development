from typing import Literal

from pydantic import BaseModel, Field

BoardColumn = Literal["todo", "in_progress", "done"]
EventType = Literal[
    "join",
    "board_state",
    "create_task",
    "task_created",
    "update_task",
    "task_updated",
    "move_task",
    "task_moved",
    "delete_task",
    "task_deleted",
    "typing",
    "user_joined",
    "user_left",
    "error",
]


class ClientEvent(BaseModel):
    type: EventType
    username: str | None = Field(default=None, max_length=100)
    task_id: int | None = None
    title: str | None = Field(default=None, max_length=255)
    column: BoardColumn | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    column: BoardColumn
    created_by: str


class ServerEvent(BaseModel):
    type: EventType
    message: str | None = None
    username: str | None = None
    users: list[str] | None = None
    tasks: list[TaskOut] | None = None
    task: TaskOut | None = None
    task_id: int | None = None
    column: BoardColumn | None = None
