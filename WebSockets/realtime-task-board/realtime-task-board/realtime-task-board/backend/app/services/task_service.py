from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.events import BoardColumn


class TaskService:
    @staticmethod
    def list_tasks(db: Session) -> list[Task]:
        return db.query(Task).order_by(Task.created_at.asc()).all()

    @staticmethod
    def create_task(db: Session, title: str, column: BoardColumn, created_by: str) -> Task:
        task = Task(title=title.strip(), column=column, created_by=created_by)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(db: Session, task_id: int, title: str) -> Task | None:
        task = db.get(Task, task_id)
        if task is None:
            return None
        task.title = title.strip()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def move_task(db: Session, task_id: int, column: BoardColumn) -> Task | None:
        task = db.get(Task, task_id)
        if task is None:
            return None
        task.column = column
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        task = db.get(Task, task_id)
        if task is None:
            return False
        db.delete(task)
        db.commit()
        return True
